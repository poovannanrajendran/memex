import os
import json
import re
import yaml
from datetime import datetime, date, timezone
from typing import Dict, List, Optional

class WikiEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

def extract_summary(content: str) -> str:
    """Extract first 2-3 sentences after frontmatter."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    content = re.sub(r'#+\s+.*', '', content)
    content = re.sub(r'\[\[(.*?)\]\]', r'\1', content)
    
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    summary = " ".join(sentences[:3])
    return summary[:500]

def build_wiki_index(output_path="wiki_index.json") -> dict:
    """
    Scan wiki/ directory and create structured index of all pages.
    """
    print("Building wiki index...")
    index = {
        "metadata": {
            "built_at": datetime.now(timezone.utc).isoformat(),
            "total_pages": 0,
            "last_commit": "unknown"
        },
        "sources": {},
        "entities": {},
        "concepts": {},
        "synthesis": {}
    }

    wiki_root = 'wiki'
    if not os.path.exists(wiki_root):
        print(f"Warning: {wiki_root} does not exist.")
        with open(output_path, 'w') as f:
            json.dump(index, f, indent=2, cls=WikiEncoder)
        return index

    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        if res.returncode == 0:
            index["metadata"]["last_commit"] = res.stdout.strip()
    except:
        pass

    exclude_files = ['index.md', 'log.md', 'README.md']
    folders = ['sources', 'entities', 'concepts', 'synthesis']

    for folder in folders:
        folder_path = os.path.join(wiki_root, folder)
        if not os.path.exists(folder_path):
            continue
        
        for root, _, files in os.walk(folder_path):
            for f in files:
                if f.endswith('.md') and f not in exclude_files:
                    file_path = os.path.join(root, f)
                    slug = os.path.splitext(f)[0]
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            raw_content = file.read()
                    except UnicodeDecodeError:
                        print(f"Warning: Skipping non-UTF8 file {file_path}")
                        continue

                    frontmatter = {}
                    title = slug.replace('_', ' ').title()
                    
                    if raw_content.startswith('---'):
                        parts = raw_content.split('---', 2)
                        if len(parts) >= 3:
                            try:
                                frontmatter = yaml.safe_load(parts[1]) or {}
                                title = frontmatter.get('title', title)
                            except Exception as e:
                                print(f"Warning: Failed to parse YAML in {file_path}: {e}")

                    summary = extract_summary(raw_content)
                    keywords = set(slug.split('_'))
                    if 'tags' in frontmatter:
                        tags = frontmatter['tags']
                        if isinstance(tags, list):
                            keywords.update([str(t).lower() for t in tags])
                        elif isinstance(tags, str):
                            keywords.update([t.strip().lower() for t in tags.split(',')])
                    
                    keywords.update(str(title).lower().split())
                    
                    word_count = len(raw_content.split())
                    
                    index[folder][slug] = {
                        "title": title,
                        "summary": summary,
                        "keywords": sorted(list(keywords)),
                        "word_count": word_count,
                        "estimated_tokens": int(word_count * 1.3),
                        "file_path": file_path,
                        "frontmatter": frontmatter
                    }
                    index["metadata"]["total_pages"] += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, cls=WikiEncoder)
    
    print(f"Index built with {index['metadata']['total_pages']} pages.")
    return index

def relevance_score(topic: str, page_title: str, page_summary: str, page_keywords: list) -> float:
    """
    Score relevance of a wiki page to a given topic (0.0 to 1.0).
    """
    topic_words = set(topic.lower().split())
    score = 0.0
    
    if any(word in str(page_title).lower() for word in topic_words):
        score += 0.5
        
    matching_keywords = [kw for kw in page_keywords if kw.lower() in topic.lower()]
    score += min(0.4, len(matching_keywords) * 0.2)

    if any(word in str(page_summary).lower() for word in topic_words):
        score += 0.2

    return min(1.0, score)

if __name__ == "__main__":
    build_wiki_index()
