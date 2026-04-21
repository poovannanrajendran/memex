import csv
import os
import re

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')[:50]

def youtube_to_raw(csv_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title', 'Untitled')
            slug = slugify(title)
            output_path = os.path.join(output_dir, f"{slug}.md")
            
            # Idempotency check: skip if file already exists
            if os.path.exists(output_path):
                print(f"Skipping (exists): {slug}.md")
                continue
            
            url = row.get('youtube_url', '')
            keywords = row.get('tags', '')
            summary = row.get('summary', '')
            transcript = row.get('transcript', '')
            
            # Truncate transcript to ~8,000 words as per TASKS.md
            transcript_words = transcript.split()
            if len(transcript_words) > 8000:
                transcript = ' '.join(transcript_words[:8000]) + "\n\n[...Transcript truncated...]"

            markdown_content = f"""---
title: "{title}"
url: "{url}"
keywords: "{keywords}"
source_type: youtube
---
## Summary
{summary if summary else "No summary provided."}

## Transcript
{transcript if transcript else "No transcript available."}
"""
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write(markdown_content)
            print(f"Created: {slug}.md")

if __name__ == "__main__":
    SOURCE_CSV = 'raw/youtube/youtube_videos_latest2.csv'
    OUTPUT_DIR = 'raw/youtube/'
    youtube_to_raw(SOURCE_CSV, OUTPUT_DIR)
