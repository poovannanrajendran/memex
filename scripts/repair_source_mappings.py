"""Repair historical completed-file mappings without Gemini calls or deleting originals."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from scripts.db import db
from scripts.indexer import build_wiki_index
from scripts.rebuild_index_md import rebuild_index


def repair():
    metadata = {}
    for page in Path('wiki/sources').glob('*.md'):
        text = page.read_text(encoding='utf-8')
        match = re.search(r'^## Source\s*\n+([^\n]+)', text, re.MULTILINE)
        if match:
            metadata.setdefault(match.group(1).strip(), []).append(page)
    with db.get_cursor() as cur:
        cur.execute("SELECT id,file_path,wiki_slug FROM ingested_files WHERE status='completed'")
        rows = cur.fetchall()
    result = {'mapped': 0, 'copied_hidden': [], 'recovered_raw_only': [], 'unavailable': []}
    for row in rows:
        path = Path(row['file_path'])
        if not path.is_file():
            result['unavailable'].append(row['id'])
            continue
        slug = row.get('wiki_slug')
        if slug and Path('wiki/sources', slug + '.md').is_file():
            continue
        candidates = metadata.get(path.name, [])
        if len(candidates) == 1 and candidates[0].stem:
            slug = candidates[0].stem
        elif len(candidates) == 1:
            slug = 'recovered_' + hashlib.sha256(str(path).encode()).hexdigest()[:16]
            shutil.copy2(candidates[0], Path('wiki/sources', slug + '.md'))
            result['copied_hidden'].append({'file_id': row['id'], 'slug': slug})
        elif not candidates:
            slug = 'recovered_' + hashlib.sha256(str(path).encode()).hexdigest()[:16]
            content = ('---\ntitle: ' + json.dumps(path.stem) + '\nsource_type: youtube\n'
                       'recovery: raw_source_only\n---\n\n'
                       '## Recovery note\n\nOriginal generated summary is unavailable. '
                       'Raw source preserved below without AI reprocessing.\n\n'
                       '## Source\n' + path.name + '\n\n## Original raw content\n\n' + path.read_text())
            Path('wiki/sources', slug + '.md').write_text(content)
            result['recovered_raw_only'].append({'file_id': row['id'], 'slug': slug})
        else:
            raise ValueError(f"Ambiguous historical source mapping for {path}")
        with db.get_cursor() as cur:
            cur.execute("UPDATE ingested_files SET wiki_slug=%s WHERE id=%s", (slug, row['id']))
        result['mapped'] += 1
    build_wiki_index()
    rebuild_index()
    return result


if __name__ == '__main__':
    from scripts.lock import pipeline_lock
    with pipeline_lock():
        print(json.dumps(repair(), indent=2))
