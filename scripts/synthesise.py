import os
import sys
import json
import re
import subprocess
from datetime import datetime
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

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
    with open(index_path, "r") as f:
        content = f.read()
    
    entry = f"- [[{slug}]] — {title}\n"
    if f"[[{slug}]]" in content:
        return

    # Add to Synthesis section
    if "## Synthesis" in content:
        new_content = content.replace("## Synthesis\n", f"## Synthesis\n{entry}")
        with open(index_path, "w") as f:
            f.write(new_content)

def add_backlinks(slug, source_slugs):
    backlink = f"\n\n## Related Synthesis\n- [[{slug}]]"
    for s_slug in source_slugs:
        # Check all possible directories
        found = False
        for folder in ['sources', 'entities', 'concepts']:
            path = f"wiki/{folder}/{s_slug}.md"
            if os.path.exists(path):
                with open(path, "a") as f:
                    f.write(backlink)
                found = True
                break

def run_synthesis(topic, client, model_name):
    print(f"Synthesising knowledge for topic: '{topic}'...")
    
    # 1. Gather context (search all wiki files for the topic keywords)
    # This is a simple implementation; ideally uses embedding search.
    keywords = topic.lower().split()
    relevant_content = []
    source_slugs_found = []
    
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
        print("No relevant wiki pages found for this topic.")
        return

    prompt = f"""
    You are a senior analyst for Poovi's Second Brain (Memex). 
    Your task is to produce a deep-dive synthesis on the topic: "{topic}".
    
    Use the following wiki pages as your primary context. Identify patterns, agreements, and contradictions.
    
    CONTEXT:
    {" ".join(relevant_content)}
    
    RULES:
    - Language: British English.
    - Professional, precise tone.
    - Do NOT hallucinate; only use the provided context.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': SynthesisSchema,
        }
    )
    
    data = response.parsed
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(data.title)
    
    # 2. Write Synthesis Page
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
    
    output_path = f"wiki/synthesis/{slug}.md"
    os.makedirs('wiki/synthesis', exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output_md)
    
    update_index(data.title, slug)
    add_backlinks(slug, data.source_slugs)
    
    # 3. Log and Commit
    log_entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n**Operation:** synthesise\n**Input:** {topic}\n**Output:** Created synthesis [[{slug}]].\n"
    with open("wiki/log.md", "a") as f:
        f.write(log_entry)
        
    subprocess.run(["git", "add", "wiki/"], check=True)
    subprocess.run(["git", "commit", "-m", f"synthesis: {topic}"], check=True)
    
    print(f"Success! Synthesis created at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/synthesise.py 'topic string'")
        sys.exit(1)
        
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    topic = sys.argv[1]
    
    run_synthesis(topic, client, model)
