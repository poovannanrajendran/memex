#!/usr/bin/env python3
"""
openclaw_ingest.py — Bulk ingest Memex wiki_index.json into Qdrant.

Pushes all 7,483 Memex pages into the Qdrant `memex-knowledge` collection
so OpenClaw agents can recall Memex knowledge via Mem0 AutoRecall.

Run once to seed, then re-run after major Memex rebuilds.

Usage:
    QDRANT_HOST=http://192.168.1.20:6333 python3 scripts/openclaw_ingest.py
    python3 scripts/openclaw_ingest.py --dry-run
    python3 scripts/openclaw_ingest.py --type synthesis  # ingest one type only
"""

import json
import os
import sys
import hashlib
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST  = os.getenv("QDRANT_HOST", "http://192.168.1.20:6333")
COLLECTION   = "memex-knowledge"
WIKI_INDEX   = Path(__file__).parent.parent / "wiki_index.json"
BATCH_SIZE   = 100
ENTRY_TYPES  = ["sources", "entities", "concepts", "synthesis"]


def stable_id(type_slug: str) -> int:
    """Deterministic integer ID from type:slug — safe for Qdrant."""
    return int(hashlib.sha256(type_slug.encode()).hexdigest()[:15], 16)


def build_text(entry: dict, entry_type: str, slug: str) -> str:
    parts = [f"[{entry_type.upper()}] {entry.get('title', slug)}"]
    if entry.get("summary"):
        parts.append(entry["summary"])
    fm = entry.get("frontmatter", {})
    if fm.get("domain"):
        parts.append(f"Domain: {fm['domain']}")
    if fm.get("entity_type"):
        parts.append(f"Entity type: {fm['entity_type']}")
    if fm.get("synthesis_type"):
        parts.append(f"Synthesis type: {fm['synthesis_type']}")
    if entry.get("keywords"):
        parts.append(f"Keywords: {', '.join(entry['keywords'][:15])}")
    tags = fm.get("tags", [])
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")
    return "\n".join(parts)


def ensure_collection(dry_run: bool):
    if dry_run:
        print(f"[dry-run] Would ensure collection: {COLLECTION}")
        return
    r = requests.get(f"{QDRANT_HOST}/collections/{COLLECTION}", timeout=5)
    if r.status_code == 404:
        resp = requests.put(
            f"{QDRANT_HOST}/collections/{COLLECTION}",
            json={"vectors": {"size": 4, "distance": "Cosine"}},  # payload-only; Mem0 handles embeddings
            timeout=10
        )
        resp.raise_for_status()
        print(f"Created collection: {COLLECTION}")
    elif r.status_code == 200:
        print(f"Collection exists: {COLLECTION} ({r.json().get('result', {}).get('points_count', '?')} points)")
    else:
        r.raise_for_status()


def push_batch(points: list, dry_run: bool) -> int:
    if dry_run:
        print(f"  [dry-run] Would push {len(points)} points")
        return len(points)
    resp = requests.put(
        f"{QDRANT_HOST}/collections/{COLLECTION}/points",
        json={"points": points},
        timeout=30
    )
    resp.raise_for_status()
    return len(points)


def ingest(type_filter: str = None, dry_run: bool = False):
    if not WIKI_INDEX.exists():
        print(f"ERROR: wiki_index.json not found at {WIKI_INDEX}")
        sys.exit(1)

    print(f"Loading wiki_index.json ({WIKI_INDEX.stat().st_size // 1024}KB)...")
    with open(WIKI_INDEX) as f:
        index = json.load(f)

    meta = index.get("metadata", {})
    print(f"Index built: {meta.get('built_at', 'unknown')} | Total pages: {meta.get('total_pages', '?')}")

    ensure_collection(dry_run)

    types_to_process = [type_filter] if type_filter else ENTRY_TYPES
    grand_total = 0

    for entry_type in types_to_process:
        entries = index.get(entry_type, {})
        if not entries:
            print(f"  {entry_type}: 0 entries — skipping")
            continue

        print(f"\n  Processing {entry_type} ({len(entries)} entries)...")
        batch = []
        type_total = 0

        for slug, entry in entries.items():
            text = build_text(entry, entry_type, slug)
            point = {
                "id": stable_id(f"{entry_type}:{slug}"),
                "vector": [0.0, 0.0, 0.0, 0.0],  # placeholder — Mem0 re-embeds on recall
                "payload": {
                    "type": entry_type,
                    "slug": slug,
                    "title": entry.get("title", slug),
                    "summary": (entry.get("summary") or "")[:500],
                    "file_path": entry.get("file_path", ""),
                    "keywords": entry.get("keywords", [])[:20],
                    "domain": entry.get("frontmatter", {}).get("domain", ""),
                    "confidence": entry.get("frontmatter", {}).get("confidence", ""),
                    "last_updated": entry.get("frontmatter", {}).get("last_updated", ""),
                    "source": "memex",
                    "text": text  # full searchable text
                }
            }
            batch.append(point)

            if len(batch) >= BATCH_SIZE:
                pushed = push_batch(batch, dry_run)
                type_total += pushed
                grand_total += pushed
                print(f"    {type_total}/{len(entries)} pushed...")
                batch = []

        if batch:
            pushed = push_batch(batch, dry_run)
            type_total += pushed
            grand_total += pushed

        print(f"  {entry_type}: {type_total} points {'(dry-run)' if dry_run else 'ingested'}")

    print(f"\n{'[dry-run] ' if dry_run else ''}Total: {grand_total} points pushed to {COLLECTION}")

    if not dry_run:
        # Verify
        r = requests.get(f"{QDRANT_HOST}/collections/{COLLECTION}", timeout=5)
        if r.ok:
            count = r.json().get("result", {}).get("points_count", "?")
            print(f"Qdrant collection {COLLECTION} now has {count} points")
        print(f"\nDashboard: {QDRANT_HOST}/dashboard")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk ingest Memex wiki_index into Qdrant")
    parser.add_argument("--type", choices=ENTRY_TYPES, help="Ingest one type only")
    parser.add_argument("--dry-run", action="store_true", help="Print counts without pushing")
    args = parser.parse_args()
    ingest(type_filter=args.type, dry_run=args.dry_run)
