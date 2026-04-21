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

# --- File Operations ---

def update_index(title, slug, category):
    index_path = "wiki/index.md"
    with open(index_path, "r") as f:
        lines = f.readlines()
    
    entry = f"- [[{slug}]] — {title}\n"
    if any(f"[[{slug}]]" in line for line in lines):
        return

    new_lines = []
    in_section = False
    added = False
    
    category_header = f"## {category}"
    for line in lines:
        new_lines.append(line)
        if category_header in line:
            in_section = True
        elif in_section and (line.startswith("##") or line.strip() == "") and not added:
            # We don't want to append at the very first empty line after header, but before the next section
            pass
        
    # Simple append for now to ensure correctness, can be refined to alphabetical later
    with open(index_path, "a") as f:
        f.write(entry)

def log_operation(title, source_file, entities, concepts):
    log_path = "wiki/log.md"
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""
## {date_now}

**Operation:** ingest
**Input:** {source_file}
**Output:** Created source summary for {title}. Entities: {', '.join([f'[[{slugify(e.name)}]]' for e in entities])}. Concepts: {', '.join([f'[[{slugify(c.name)}]]' for c in concepts])}.
**Notes:** Automated ingestion via Gemini API.
"""
    with open(log_path, "a") as f:
        f.write(entry)

def commit_changes(message):
    subprocess.run(["git", "add", "wiki/"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

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

# --- Main Ingest Logic ---

def ingest_file(file_path, client, model_name):
    print(f"Ingesting: {file_path}...")
    
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
    - Link related concepts using their names.
    
    SOURCE CONTENT:
    {content}
    """
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': IngestionSchema,
        }
    )
    
    data = response.parsed
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

    # 2. Process Entities
    for e in data.entities:
        e_slug = slugify(e.name)
        e_path = f"wiki/entities/{e_slug}.md"
        
        # If exists, we'd ideally merge, but for this version we create if new
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

    # 3. Process Concepts
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

    log_operation(data.title, os.path.basename(file_path), data.entities, data.concepts)
    commit_changes(f"ingest: {data.title}")
    print(f"Success: {data.title}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <file_or_folder>")
        sys.exit(1)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    target = sys.argv[1]
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    if os.path.isfile(target):
        ingest_file(target, client, model)
    elif os.path.isdir(target):
        # Sort files to ensure deterministic ingestion
        files = sorted([f for f in os.listdir(target) if f.endswith((".md", ".txt", ".json", ".html"))])
        for f in files:
            ingest_file(os.path.join(target, f), client, model)
