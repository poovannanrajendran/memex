import sys
import os
import re
import trafilatura
from pathlib import Path

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')[:50]

def add_url(url):
    print(f"Fetching content from: {url}...")
    
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print(f"Error: Could not download content from {url}")
        return

    content = trafilatura.extract(downloaded, include_comments=False, include_tables=True, no_fallback=False)
    if not content:
        print(f"Error: Could not extract meaningful text from {url}")
        return

    # Try to get a title
    title_match = re.search(r'title>(.*?)</title>', downloaded, re.IGNORECASE)
    title = title_match.group(1) if title_match else "Web Article"
    
    slug = slugify(title)
    output_path = Path("raw/articles") / f"{slug}.md"
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown_content = f"""---
title: "{title.strip()}"
source_type: article
url: "{url}"
---

{content}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"✅ Success! Content saved to {output_path}")
    print("The librarian will ingest this in the next automated run.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_url.py <URL>")
        sys.exit(1)
    
    add_url(sys.argv[1])
