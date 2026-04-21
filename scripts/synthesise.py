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

def extract_claims(page_content: str, client, run_id=None, max_tokens_before_summarise=5000) -> str:
    """
    Extract key claims from a wiki page using Flash model (cheap).
    """
    start_time = time.time()
    
    if len(page_content) > 10000:
        page_content = page_content[:10000] + "\n[... truncated ...]"
                                                                                                                               
    prompt = f"""Extract 3–5 key claims, facts, or insights from this wiki page.
    Output format: bullet list only, one sentence per bullet.                                                                
    Be concise and specific.                                                                                                 
    
    PAGE:                                                                                                                    
    {page_content}
    """                                                                                                                      
   
    try:                                                                                                                     
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        claims = response.text
        duration_ms = int((time.time() - start_time) * 1000)                                                                 
   
        if run_id:                                                                                                           
            input_tokens = getattr(response, 'usage_metadata', None).prompt_token_count if hasattr(response, 'usage_metadata') else 0                                                                                                     
            output_tokens = getattr(response, 'usage_metadata', None).candidates_token_count if hasattr(response, 'usage_metadata') else 0                                                                                                     
            db.log_ai_call(run_id, 'synthesise_extract_claims', 'gemini-2.5-flash', 'extract_claims', input_tokens, output_tokens, duration_ms, success=True)                                                                                    
   
        return claims                                                                                                        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        if run_id:                                                                                                           
            db.log_ai_call(run_id, 'synthesise_extract_claims', 'gemini-2.5-flash', 'extract_claims', 0, 0, duration_ms, success=False, error_message=str(e))                                                                                         
        return f"[Failed to extract claims. Original content: {page_content[:500]}...]"

def determine_model(topic: str, num_pages: int, total_content_tokens: int) -> str:
    """
    Choose synthesis model based on task complexity.
    """
    if num_pages <= 3 and total_content_tokens < 8000:                                                                       
        return "gemini-2.5-flash"                                                                                            
    if num_pages <= 5 and total_content_tokens < 15000:
        return "gemini-2.5-flash"                                                                                            
    return "gemini-2.5-pro"

def run_synthesis(topic, client, model_name, run_id=None, mode='flex'):
    """
    Synthesise knowledge on a given topic using index-based filtering.
    """
    print(f"Synthesising knowledge for topic: '{topic}'...")
    start_time = time.time()
    
    # Load wiki index
    if not os.path.exists("wiki_index.json"):
        print("Wiki index not found. Building...")
        from indexer import build_wiki_index
        build_wiki_index()
        
    with open("wiki_index.json", "r") as f:
        wiki_index = json.load(f)

    # 1. FILTER: Find relevant pages using index
    from indexer import relevance_score
    candidates = []
    
    for folder in ["sources", "concepts", "entities"]:
        for slug, page_meta in wiki_index.get(folder, {}).items():
            score = relevance_score(
                topic,
                page_meta["title"],
                page_meta["summary"],
                page_meta.get("keywords", [])
            )
            if score > 0.3:
                candidates.append((slug, folder, score, page_meta))

    if not candidates:
        print("No relevant wiki pages found.")
        return

    # Sort by relevance, take top 10
    candidates.sort(key=lambda x: x[2], reverse=True)
    top_pages = candidates[:10]
    
    # CHECK CACHE
    from synthesis_cache import SynthesisCache
    cache = SynthesisCache()
    cache_hash = cache.get_hash(topic, [slug for slug, _, _, _ in top_pages])
    
    if cache.exists(cache_hash):
        cached = cache.get(cache_hash)
        print(f"Synthesis already exists: [[{cached['synthesis_slug']}]]")
        print(f"(Cached at {cached['cached_at']})")
        return

    print(f"Found {len(top_pages)} relevant pages (filtered from {len(wiki_index.get('sources',{})) + len(wiki_index.get('concepts',{})) + len(wiki_index.get('entities',[]))} total)")

    # 2. EXTRACT: Load only the top pages and extract claims
    relevant_content = []
    source_slugs_found = []
    
    for slug, folder, score, page_meta in top_pages:
        path = page_meta["file_path"]
        with open(path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            
        claims = extract_claims(full_content, client, run_id)
        relevant_content.append(f"FILE: {slug}\nCLAIMS:\n{claims}\n---")
        source_slugs_found.append(slug)

    # 3. DETERMINE MODEL
    model_for_synthesis = determine_model(
        topic=topic,
        num_pages=len(top_pages),
        total_content_tokens=sum(len(c.split()) * 1.3 for c in relevant_content)
    )
    
    is_batch = (mode == 'batch')

    # 4. SYNTHESISE
    prompt = f"""
    You are a senior analyst for Poovi's Second Brain (Memex). 
    Your task is to produce a synthesis on the topic: "{topic}".
    
    CONTEXT (key claims extracted from wiki):
    {" ".join(relevant_content)}
    """

    try:
        response = client.models.generate_content(
            model=model_for_synthesis,
            contents=prompt,
            config={'response_mime_type': 'application/json', 'response_schema': SynthesisSchema}
        )
        data = response.parsed
        duration_ms = int((time.time() - start_time) * 1000)
        
        if run_id:
            input_tokens = getattr(response, 'usage_metadata', None).prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = getattr(response, 'usage_metadata', None).candidates_token_count if hasattr(response, 'usage_metadata') else 0
            db.log_ai_call(run_id, 'synthesise', model_for_synthesis, 'synthesise_topic', input_tokens, output_tokens, duration_ms, is_batch=is_batch)

    except Exception as e:
        if run_id:
            db.log_ai_call(run_id, 'synthesise', model_for_synthesis, 'synthesise_topic', 0, 0, int((time.time()-start_time)*1000), success=False, error_message=str(e), is_batch=is_batch)
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
    
    # UPDATE CACHE
    cache.set(cache_hash, slug, topic, source_slugs_found)
    
    subprocess.run(["git", "add", "wiki/"], check=True)
    subprocess.run(["git", "commit", "-m", f"synthesis: {topic}"], check=True)
    print(f"Success! Created [[{slug}]]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/synthesise.py <topic> [run_id]")
        sys.exit(1)
        
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # We now dynamically determine model, but can use synthesis model from env as preference
    mode = os.getenv("GEMINI_SYNTHESIS_MODE", "flex")
    
    topic = sys.argv[1]
    run_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Default model from env if not determined otherwise
    model = os.getenv("GEMINI_SYNTHESIS_MODEL", "gemini-2.5-pro")
    
    run_synthesis(topic, client, model, run_id, mode)
