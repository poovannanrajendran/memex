import os
import re
import yaml
from datetime import datetime

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

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
- TBD

## Related concepts
- TBD
"""

ENTITY_STUB = """---
title: "{title}"
entity_type: person
tags: ["stub"]
last_updated: {date}
---

## Overview
Stub for {title}.

## Role in this knowledge base
TBD

## Key facts
- TBD

## Sources
- TBD

## Related concepts
- TBD
"""

def autofix():
    print("Starting link autofix...")
    wiki_files = []
    for root, dirs, files in os.walk('wiki'):
        for f in files:
            if f.endswith('.md') and f not in ['index.md', 'log.md', 'README.md']:
                wiki_files.append(os.path.join(root, f))
    
    all_slugs = {os.path.splitext(os.path.basename(f))[0]: f for f in wiki_files}
    
    broken_links = {} # slug -> original_name
    
    for fpath in wiki_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                slug = slugify(link)
                if slug not in all_slugs:
                    if slug not in broken_links:
                        # Determine if it's likely an entity or concept
                        # Very basic heuristic: if it's in an entity file, it might be an entity
                        category = "concepts"
                        if "wiki/entities" in fpath:
                            category = "entities"
                        
                        broken_links[slug] = {
                            "name": link,
                            "category": category,
                            "found_in": fpath
                        }

    date_str = datetime.now().strftime("%Y-%m-%d")
    fixed_count = 0

    for slug, info in broken_links.items():
        title = info["name"].replace('_', ' ').title()
        category = info["category"]
        target_path = f"wiki/{category}/{slug}.md"
        
        # Double check if it exists (case sensitivity or other folder)
        if os.path.exists(target_path):
            continue
            
        print(f"Creating stub for [[{info['name']}]] at {target_path}")
        
        if category == "entities":
            content = ENTITY_STUB.format(title=title, date=date_str)
        else:
            content = CONCEPT_STUB.format(title=title, date=date_str)
            
        with open(target_path, "w", encoding='utf-8') as f:
            f.write(content)
        fixed_count += 1

    print(f"Finished. Created {fixed_count} stub files.")
    
    if fixed_count > 0:
        try:
            from indexer import build_wiki_index
            build_wiki_index()
        except ImportError:
            pass

if __name__ == "__main__":
    autofix()
