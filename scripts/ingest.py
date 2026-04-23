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

class Entity(BaseModel):
    name: str
    type: str = Field(description="person | organisation | tool | product")
    overview: str = Field(description="2-3 sentence description of who/what this is")
    role: str = Field(description="Why this entity appears in the context of insurance/AI/Poovi's work")
    key_fact: str = Field(description="One specific key fact about this entity from the source")
    related_concepts: List[str] = Field(default_factory=list)

class Concept(BaseModel):
    name: str
    domain: str = Field(description="insurance | ai-engineering | productivity | podcast | general")
    definition: str = Field(description="Clear, plain-English definition (1-3 sentences)")
    importance: str = Field(description="Relevance to Lloyd's, AI, or personal projects")
    properties: List[str] = Field(description="Key properties or components")
    contradictions: Optional[str] = Field(None, description="Any debates or conflicting info found in this source")
    related_concepts: List[str] = Field(default_factory=list)

class IngestionSchema(BaseModel):
    title: str
    source_type: str = Field(description="article | pdf | transcript | youtube")
    url: Optional[str] = Field(None)
    summary: str = Field(description="2-4 sentence summary in plain prose")
    key_claims: List[str]
    entities: List[Entity]
    concepts: List[Concept]
    tags: List[str]
    contradictions_flag: Optional[str] = Field(None, description="Flag any claims that conflict with existing wiki knowledge if known")

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

# --- Templates ---

SOURCE_TEMPLATE = """---
title: "{title}"
source_type: {source_type}
url: "{url}"
ingested: {date}
confidence: high
tags: {tags}
---

## Summary
{summary}

## Key claims
{key_claims}

## Entities mentioned
{entities}

## Concepts covered
{concepts}

## Contradictions or open questions
{contradictions}

## Source
{source_info}
"""

ENTITY_TEMPLATE = """---
title: "{title}"
entity_type: {entity_type}
tags: {tags}
last_updated: {date}
---

## Overview
{overview}

## Role in this knowledge base
{role}

## Key facts
- {fact}

## Sources
- [[{source_slug}]]

## Related concepts
{related_concepts}
"""

CONCEPT_TEMPLATE = """---
title: "{title}"
domain: {domain}
tags: {tags}
last_updated: {date}
confidence: high
---

## Definition
{definition}

## Why it matters (in Poovi's context)
{importance}

## Key properties or components
{properties}

## Contradictions or debates
{contradictions}

## Sources
- [[{source_slug}]]

## Related concepts
{related_concepts}
"""

# --- File Operations ---

def update_index(title, slug, category):
    index_path = "wiki/index.md"
    if not os.path.exists(index_path):
        return
    with open(index_path, "r") as f:
        content = f.read()
    
    entry = f"- [[{slug}]] — {title}\n"
    if f"[[{slug}]]" in content:
        return

    section_header = f"## {category}"
    if section_header in content:
        new_content = content.replace(f"{section_header}\n", f"{section_header}\n{entry}")
        with open(index_path, "w") as f:
            f.write(new_content)

def log_operation(title, source_file, entities, concepts):
    log_path = "wiki/log.md"
    if not os.path.exists(log_path):
        return
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {date_now}\n\n**Operation:** ingest\n**Input:** {source_file}\n**Output:** Created source summary for {title}.\n"
    with open(log_path, "a") as f:
        f.write(entry)

def commit_changes(message):
    subprocess.run(["git", "add", "wiki/"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

# --- Main Ingest Logic ---

def ingest_file(file_path, client, model_name, run_id=None, file_id=None):
    print(f"Ingesting: {file_path}...")
    start_time = time.time()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    prompt = f"""
    Analyse the following source document and extract structured information for a personal knowledge base (Second Brain).
    
    RULES:
    - Language: British English (organise, analyse, recognise, programme)
    - Be precise and professional.
    - Extract entities (people, organisations, tools, products).
    - Extract concepts (ideas, frameworks, theories, patterns).
    - Identify key claims and summaries.
    
    SOURCE CONTENT:
    {content}
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': IngestionSchema,
            }
        )
        
        data = response.parsed
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log AI Call if run_id is provided and not '0'
        if run_id and run_id != "0":
            # Note: Token counts might need model-specific retrieval if not in response
            # Assuming metadata access or estimation
            input_tokens = getattr(response, 'usage_metadata', None).prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = getattr(response, 'usage_metadata', None).candidates_token_count if hasattr(response, 'usage_metadata') else 0
            fid = file_id if file_id != "0" else None
            db.log_ai_call(run_id, 'ingest', model_name, 'ingest_document', input_tokens, output_tokens, duration_ms, success=True, file_id=fid)

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        if run_id and run_id != "0":
            fid = file_id if file_id != "0" else None
            db.log_ai_call(run_id, 'ingest', model_name, 'ingest_document', 0, 0, duration_ms, success=False, file_id=fid, error_message=str(e))
        raise e

    date_str = datetime.now().strftime("%Y-%m-%d")
    source_slug = slugify(data.title)
    
    # 1. Write Source Summary
    source_md = SOURCE_TEMPLATE.format(
        title=data.title,
        source_type=data.source_type,
        url=data.url or "",
        date=date_str,
        tags=json.dumps(data.tags),
        summary=data.summary,
        key_claims="\n".join([f"- {c}" for c in data.key_claims]),
        entities="\n".join([f"- [[{slugify(e.name)}]] — {e.role}" for e in data.entities]),
        concepts="\n".join([f"- [[{slugify(c.name)}]] — {c.importance}" for c in data.concepts]),
        contradictions=data.contradictions_flag or "None identified.",
        source_info=os.path.basename(file_path)
    )
    
    with open(f"wiki/sources/{source_slug}.md", "w") as f:
        f.write(source_md)
    update_index(data.title, source_slug, "Sources")

    pages_created = 1
    entities_count = 0
    concepts_count = 0

    # 2. Process Entities
    for e in data.entities:
        e_slug = slugify(e.name)
        e_path = f"wiki/entities/{e_slug}.md"
        if not os.path.exists(e_path):
            e_md = ENTITY_TEMPLATE.format(
                title=e.name,
                entity_type=e.type,
                tags=json.dumps([e.type]),
                date=date_str,
                overview=e.overview,
                role=e.role,
                fact=e.key_fact,
                source_slug=source_slug,
                related_concepts="\n".join([f"- [[{slugify(rc)}]]" for rc in e.related_concepts])
            )
            with open(e_path, "w") as f:
                f.write(e_md)
            update_index(e.name, e_slug, "Entities")
            pages_created += 1
        entities_count += 1

    # 3. Process Concepts
    all_related = set()
    for c in data.concepts:
        c_slug = slugify(c.name)
        c_path = f"wiki/concepts/{c_slug}.md"
        if not os.path.exists(c_path):
            c_md = CONCEPT_TEMPLATE.format(
                title=c.name,
                domain=c.domain,
                tags=json.dumps([c.domain]),
                date=date_str,
                definition=c.definition,
                importance=c.importance,
                properties="\n".join([f"- {p}" for p in c.properties]),
                contradictions=c.contradictions or "None.",
                source_slug=source_slug,
                related_concepts="\n".join([f"- [[{slugify(rc)}]]" for rc in c.related_concepts])
            )
            with open(c_path, "w") as f:
                f.write(c_md)
            update_index(c.name, c_slug, "Concepts")
            pages_created += 1
        concepts_count += 1
        for rc in c.related_concepts:
            all_related.add(rc)
            
    for e in data.entities:
        for rc in e.related_concepts:
            all_related.add(rc)

    # 4. Create stubs for missing related concepts
    CONCEPT_STUB = """---
title: "{title}"
domain: general
tags: ["stub"]
last_updated: {date}
confidence: low
---

## Definition
Stub for {title}.

## Why it matters (in Poovi's context)
TBD

## Key properties or components
- TBD

## Contradictions or debates
None.

## Sources
- [[{source_slug}]]

## Related concepts
- TBD
"""
    for rc in all_related:
        rc_slug = slugify(rc)
        # Check if it exists anywhere in wiki/
        exists = False
        for folder in ['concepts', 'entities', 'sources']:
            if os.path.exists(f"wiki/{folder}/{rc_slug}.md"):
                exists = True
                break
        
        if not exists:
            rc_path = f"wiki/concepts/{rc_slug}.md"
            rc_md = CONCEPT_STUB.format(
                title=rc.title() if len(rc) > 3 else rc.upper(),
                date=date_str,
                source_slug=source_slug
            )
            with open(rc_path, "w") as f:
                f.write(rc_md)
            update_index(rc, rc_slug, "Concepts")
            pages_created += 1

    # Update file status in DB
    if file_id and file_id != "0":
        db.update_file(file_id, 'completed', wiki_pages_created=pages_created, entities_extracted=entities_count, concepts_extracted=concepts_count)

    log_operation(data.title, os.path.basename(file_path), data.entities, data.concepts)
    commit_changes(f"ingest: {data.title}")
    
    # Regenerate index after each ingest
    try:
        from indexer import build_wiki_index
        build_wiki_index()
        from rebuild_index_md import rebuild_index
        rebuild_index()
    except Exception as e:
        print(f"Warning: Failed to rebuild wiki index: {e}")
        
    print(f"Success: {data.title}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <file_path> [run_id] [file_id]")
        sys.exit(1)
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    # Use ingest model from env, or command line override
    model = sys.argv[4] if len(sys.argv) > 4 else os.getenv("GEMINI_INGEST_MODEL", "gemini-2.5-flash-lite")
    
    target_file = sys.argv[1]
    run_id = sys.argv[2] if len(sys.argv) > 2 else None
    file_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    ingest_file(target_file, client, model, run_id, file_id)
