import os
import re
from datetime import datetime

def slugify(text):
    s = text.lower().strip()
    s = s.replace("'", "")
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

def run_lint():
    report = []
    report.append(f"# Second Brain Lint Report — {datetime.now().strftime('%Y-%m-%d')}\n")
    
    wiki_files = []
    for root, dirs, files in os.walk('wiki'):
        for f in files:
            if f.endswith('.md') and f not in ['index.md', 'log.md', 'README.md']:
                wiki_files.append(os.path.join(root, f))
    
    # 1. Broken Wikilinks
    broken_links = []
    all_slugs = [os.path.splitext(os.path.basename(f))[0] for f in wiki_files]
    
    for fpath in wiki_files:
        with open(fpath, 'r') as f:
            content = f.read()
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                link_slug = slugify(link)
                if link_slug not in all_slugs:
                    broken_links.append(f"{fpath}: [[{link}]]")
    
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
            with open(fpath, 'r') as f:
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
    with open('wiki/index.md', 'r') as f:
        index_content = f.read()
    for slug in all_slugs:
        if f"[[{slug}]]" not in index_content:
            missing_index.append(slug)
            
    if missing_index:
        report.append("\n## Warnings: Missing Index Entries")
        for mi in missing_index:
            report.append(f"- [[{mi}]]")

    report_content = "\n".join(report)
    report_path = f"output/lint-{datetime.now().strftime('%Y-%m-%d')}.md"
    os.makedirs('output', exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"Lint complete. Report written to {report_path}")
    print(f"Found {len(broken_links)} broken links, {len(orphans)} orphans, and {len(missing_index)} missing index entries.")

if __name__ == "__main__":
    run_lint()
