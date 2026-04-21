import json
import os

def rebuild_index(index_json_path="wiki_index.json", index_md_path="wiki/index.md"):
    if not os.path.exists(index_json_path):
        print(f"Error: {index_json_path} not found.")
        return

    with open(index_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    header = """---
title: memex — Poovi's Second Brain
---

Welcome to **memex**, an AI-maintained personal knowledge base built on the [Karpathy LLM Wiki pattern](https://karpathy.ai).

This is a **working, living system** — sources are ingested daily, concepts are extracted automatically, and synthesis pages compound knowledge over time.

## 🏛️ Architecture
Every new source flows through three layers:
1. **Raw** — Immutable source inbox (articles, PDFs, transcripts).
2. **Wiki** — Agent-maintained knowledge network (entities, concepts, synthesis).
3. **Synthesis** — Cross-source analysis and deep dives.

The entire system is powered by **Google's Gemini 2.5 API** with a 1M+ token context window.

## 🔍 What You'll Find Here
- **Lloyd's Market Intelligence** — Specialty insurance research and insights.
- **AI Engineering & Agent Systems** — Frameworks, patterns, and production builds.
- **Mahabharata Moments Podcast** — Research and narrative development.

## 🌐 Explore
- [[readme]] — Project README.
- [[log]] — Operation Log.
- [[lloyds_of_london]] — Insurance market research.
- [[ai_agent_frameworks]] — Agent design patterns.
- [[deep_dive_synthesis_ai_agent_workflow_design_patterns]] — Recent synthesis.
"""

    sections = {
        "sources": "## Sources",
        "entities": "## Entities",
        "concepts": "## Concepts",
        "synthesis": "## Synthesis"
    }

    content = [header]

    for key, title in sections.items():
        if key in data and data[key]:
            content.append(f"\n{title}")
            # Sort items by title
            items = sorted(data[key].items(), key=lambda x: x[1].get('title', x[0]))
            for slug, info in items:
                display_title = info.get('title', slug.replace('_', ' ').title())
                content.append(f"- [[{slug}]] — {display_title}")

    footer = """
---

Built with [Quartz](https://quartz.jzhao.xyz/) and deployed on [Vercel](https://vercel.com/).  
Source: [github.com/poovannanrajendran/memex](https://github.com/poovannanrajendran/memex)
"""
    content.append(footer)

    with open(index_md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    
    print(f"Rebuilt {index_md_path} with {data['metadata']['total_pages']} entries.")

if __name__ == "__main__":
    rebuild_index()
