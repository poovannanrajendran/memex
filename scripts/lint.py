import os
import re
import sys
import yaml
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# We only import db if it exists, for standalone usage resilience
try:
    from db import db
except ImportError:
    db = None

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

def check_staleness(client, model_name, title, content):
    """Use Gemini with Google Search Grounding to check if claims are superseded."""
    prompt = f"""
    The following is a wiki page from a personal knowledge base titled '{title}'.
    It is over 180 days old. 
    Use Google Search to check if the key claims or facts in this document have been superseded by more recent information.
    Keep your response brief, stating either 'Still accurate' or noting specific updates/superseded facts.
    
    PAGE CONTENT:
    {content[:3000]}
    """
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                'tools': [{'google_search': {}}]
            }
        )
        return response.text.replace('\n', ' ').strip()
    except Exception as e:
        return f"Could not verify staleness via Search Grounding: {e}"

def run_lint(run_id=None):
    print("Running lint health check...")
    report = []
    report.append(f"# Second Brain Lint Report — {datetime.now().strftime('%Y-%m-%d')}\n")
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = None
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
        except ImportError:
            pass
            
    # Default to a model that supports grounding
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    wiki_files = []
    for root, dirs, files in os.walk('wiki'):
        for f in files:
            if f.endswith('.md') and f not in ['index.md', 'log.md', 'README.md']:
                wiki_files.append(os.path.join(root, f))
    
    # 1. Broken Wikilinks
    broken_links = []
    all_slugs = [os.path.splitext(os.path.basename(f))[0] for f in wiki_files]
    
    stale_pages = []
    now = datetime.now()
    
    for fpath in wiki_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check broken links
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                link_slug = slugify(link)
                if link_slug not in all_slugs:
                    broken_links.append(f"{fpath}: [[{link}]]")
                    
            # Check Staleness
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if frontmatter and isinstance(frontmatter, dict):
                            # Ensure we have a string to parse
                            date_str = str(frontmatter.get('ingested') or frontmatter.get('last_updated') or "")
                            if date_str:
                                # handle YYYY-MM-DD
                                file_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                if (now - file_date).days > 180:
                                    title = frontmatter.get('title', os.path.basename(fpath))
                                    stale_pages.append((fpath, title, parts[2]))
                    except Exception as e:
                        pass
    
    if broken_links:
        report.append("## Errors: Broken Wikilinks")
        for bl in broken_links:
            report.append(f"- {bl}")
    
    # 2. Orphan Pages
    orphans = []
    for slug in all_slugs:
        found = False
        for fpath in wiki_files:
            if slug in fpath: continue
            with open(fpath, 'r', encoding='utf-8') as f:
                if f"[[{slug}]]" in f.read():
                    found = True
                    break
        if not found:
            orphans.append(slug)
            
    if orphans:
        report.append("\n## Warnings: Orphan Pages")
        for o in orphans:
            report.append(f"- [[{o}]]")
            
    # 3. Missing Index Entries
    missing_index = []
    index_content = ""
    if os.path.exists('wiki/index.md'):
        with open('wiki/index.md', 'r', encoding='utf-8') as f:
            index_content = f.read()
    for slug in all_slugs:
        if f"[[{slug}]]" not in index_content:
            missing_index.append(slug)
            
    if missing_index:
        report.append("\n## Warnings: Missing Index Entries")
        for mi in missing_index:
            report.append(f"- [[{mi}]]")

    # 4. Staleness
    if stale_pages:
        report.append("\n## Warnings: Stale Pages (>180 days old)")
        for fpath, title, page_content in stale_pages:
            report.append(f"- **{fpath}** ({title})")
            if client:
                print(f"Checking staleness for {title} via Search Grounding...")
                grounding_result = check_staleness(client, model, title, page_content)
                report.append(f"  - *Search Grounding Check:* {grounding_result}")

    report_content = "\n".join(report)
    os.makedirs('output', exist_ok=True)
    report_path = f"output/lint-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    summary = f"Found {len(broken_links)} broken links, {len(orphans)} orphans, {len(missing_index)} missing index entries, and {len(stale_pages)} stale pages."
    print(f"Lint complete. {summary}")

if __name__ == "__main__":
    run_id = sys.argv[1] if len(sys.argv) > 1 else None
    run_lint(run_id)
