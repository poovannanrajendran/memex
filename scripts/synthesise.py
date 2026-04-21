import os
import sys
import json
import re
import subprocess
import time
from datetime import datetime
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from db import db

load_dotenv()

# --- Configuration & Models ---

class SynthesisSchema(BaseModel):
    title: str
    synthesis_type: str = Field(description="comparison | timeline | deep-dive | contradiction-resolution")
    thesis: str = Field(description="One sentence establishing what this synthesis establishes")
    analysis: str = Field(description="3-8 paragraphs of cross-source reasoning and prose")
    conclusions: List[str]
    open_questions: List[str]
    source_slugs: List[str] = Field(description="List of wiki source slugs used")

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

# --- Templates ---

SYNTHESIS_TEMPLATE = """---
title: "{title}"
synthesis_type: {synthesis_type}
sources: {sources}
created: {date}
---

## Thesis
{thesis}

## Analysis
{analysis}

## Conclusions
{conclusions}

## Open questions
{open_questions}

## Sources used
{sources_used}
"""

# --- Logic ---

def update_index(title, slug):
    index_path = "wiki/index.md"
    if not os.path.exists(index_path): return
    with open(index_path, "r") as f:
        content = f.read()
    
    entry = f"- [[{slug}]] — {title}\n"
    if f"[[{slug}]]" in content: return

    if "## Synthesis" in content:
        new_content = content.replace("## Synthesis\n", f"## Synthesis\n{entry}")
        with open(index_path, "w") as f:
            f.write(new_content)

def add_backlinks(slug, source_slugs):
    backlink = f"\n\n## Related Synthesis\n- [[{slug}]]"
    for s_slug in source_slugs:
        for folder in ['sources', 'entities', 'concepts']:
            path = f"wiki/{folder}/{s_slug}.md"
            if os.path.exists(path):
                with open(path, "a") as f:
                    f.write(backlink)
                break

def run_synthesis(topic, client, model_name, run_id=None):
    print(f"Synthesising knowledge for topic: '{topic}'...")
    start_time = time.time()
    
    relevant_content = []
    source_slugs_found = []
    keywords = topic.lower().split()
    
    for root, dirs, files in os.walk('wiki'):
        for f in files:
            if f.endswith('.md') and f not in ['index.md', 'log.md', 'README.md']:
                path = os.path.join(root, f)
                with open(path, 'r') as file:
                    text = file.read()
                    if any(kw in text.lower() for kw in keywords):
                        relevant_content.append(f"FILE: {f}\nCONTENT:\n{text}\n---")
                        source_slugs_found.append(os.path.splitext(f)[0])

    if not relevant_content:
        print("No relevant wiki pages found.")
        return

    prompt = f"""
    You are a senior analyst for Poovi's Second Brain (Memex). 
    Your task is to produce a deep-dive synthesis on the topic: "{topic}".
    CONTEXT:
    {" ".join(relevant_content)}
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={'response_mime_type': 'application/json', 'response_schema': SynthesisSchema}
        )
        data = response.parsed
        duration_ms = int((time.time() - start_time) * 1000)
        
        if run_id:
            input_tokens = getattr(response, 'usage_metadata', None).prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = getattr(response, 'usage_metadata', None).candidates_token_count if hasattr(response, 'usage_metadata') else 0
            db.log_ai_call(run_id, 'synthesise', model_name, 'synthesise_topic', input_tokens, output_tokens, duration_ms)

    except Exception as e:
        if run_id:
            db.log_ai_call(run_id, 'synthesise', model_name, 'synthesise_topic', 0, 0, int((time.time()-start_time)*1000), success=False, error_message=str(e))
        raise e

    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(data.title)
    
    output_md = SYNTHESIS_TEMPLATE.format(
        title=data.title,
        synthesis_type=data.synthesis_type,
        sources=json.dumps(data.source_slugs),
        date=date_str,
        thesis=data.thesis,
        analysis=data.analysis,
        conclusions="\n".join([f"- {c}" for c in data.conclusions]),
        open_questions="\n".join([f"- {q}" for q in data.open_questions]),
        sources_used="\n".join([f"- [[{s}]]" for s in data.source_slugs])
    )
    
    os.makedirs('wiki/synthesis', exist_ok=True)
    with open(f"wiki/synthesis/{slug}.md", "w") as f:
        f.write(output_md)
    
    update_index(data.title, slug)
    add_backlinks(slug, data.source_slugs)
    subprocess.run(["git", "add", "wiki/"], check=True)
    subprocess.run(["git", "commit", "-m", f"synthesis: {topic}"], check=True)
    print(f"Success! Created [[{slug}]]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/synthesise.py <topic> [run_id]")
        sys.exit(1)
        
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    
    topic = sys.argv[1]
    run_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_synthesis(topic, client, model, run_id)
