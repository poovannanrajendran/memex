#!/usr/bin/env python3
"""
Memex YouTube Catch-Up Loader
Processes historical backlog of YouTube liked videos into the Memex knowledge base.
Ensures resilience: Each video is committed in the DB immediately upon successful ingestion.
If interrupted or shutdown, re-running resumes from the exact point of interruption.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root and scripts dir to path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "scripts"))
sys.path.insert(0, str(PROJECT_DIR))

from youtube_sync import (
    YouTubeSyncManager,
    is_usable_content,
    format_video_markdown,
    DEFAULT_YOUTUBE_DB_URL,
)
from db import db

def run_catchup(batch_size: int = 10, pause_sec: float = 1.0):
    print("=" * 60)
    print("🚀 Starting Memex YouTube Catch-Up Load")
    print("=" * 60)

    mgr = YouTubeSyncManager()
    
    # 1. Fetch all unprocessed records
    print("\n🔍 Fetching unprocessed records from YouTube staging database...")
    all_unprocessed = mgr.fetch_unprocessed(limit=None)
    total_found = len(all_unprocessed)
    print(f"Found {total_found} unprocessed videos in total.")

    if total_found == 0:
        print("✅ No unprocessed videos found. Everything is up to date!")
        return

    # 2. Segregate viable candidates from non-viable records (e.g. music/shorts with no text)
    viable_candidates = []
    non_viable_count = 0

    for v in all_unprocessed:
        v_id = v.get("video_id")
        transcript = v.get("transcript")
        description = v.get("description")

        has_transcript = bool(transcript and transcript != "No transcript available" and len(transcript.strip()) > 50)
        has_desc = bool(description and is_usable_content(description))

        if has_transcript or has_desc:
            viable_candidates.append(v)
        else:
            mgr.mark_processed(v_id)
            non_viable_count += 1

    print(f"🧹 Filtered & marked {non_viable_count} non-viable videos (shorts/music with no text) as processed.")
    print(f"🎯 Viable videos queued for AI ingestion: {len(viable_candidates)}")

    if not viable_candidates:
        print("✅ All remaining videos were non-viable. Queue cleared!")
        return

    # 3. Create Memex Pipeline Run for tracking
    run_id = db.create_run(triggered_by='manual', trigger_source='youtube_catchup')
    print(f"📊 Created pipeline run: {run_id}")

    raw_dir = PROJECT_DIR / "raw" / "youtube"
    raw_dir.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    failed_count = 0

    primary_model = os.getenv("GEMINI_INGEST_MODEL", "gemini-2.5-flash-lite")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

    print(f"\n🧠 Ingesting {len(viable_candidates)} videos using {primary_model}...")

    for idx, video in enumerate(viable_candidates, 1):
        v_id = video.get("video_id")
        title = video.get("title", "Untitled")
        print(f"\n[{idx}/{len(viable_candidates)}] Processing: {title[:50]} ({v_id})")

        safe_title = "".join([c if c.isalnum() else "_" for c in title])[:40].strip("_")
        target_path = raw_dir / f"{v_id}_{safe_title}.md"

        # Format markdown
        md_text = format_video_markdown(video)
        target_path.write_text(md_text, encoding="utf-8")

        # Register file in Memex DB
        file_id = db.register_file(run_id, str(target_path), "youtube")
        step_id = db.start_step(run_id, 'ingest', file_id)

        # Execute ingestion
        cmd = [sys.executable, str(PROJECT_DIR / "scripts" / "ingest.py"), str(target_path), str(run_id), str(file_id), primary_model]
        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0:
            if "RESOURCE_EXHAUSTED" in res.stderr or "429" in res.stderr:
                print(f"⚠️ Primary model {primary_model} exhausted. Retrying with fallback {fallback_model}...")
                cmd[-1] = fallback_model
                res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode == 0:
            db.complete_step(step_id, 'completed', output_summary=f"Ingested {target_path.name}")
            mgr.mark_processed(v_id)
            processed_count += 1
            print(f"   ✅ Ingested successfully & marked isprocessed=True in YouTube DB.")
        else:
            err_msg = res.stderr or res.stdout
            print(f"   ❌ Ingestion failed: {err_msg[:200]}")
            db.complete_step(step_id, 'failed', error_message=err_msg)
            failed_count += 1
            # Leave isprocessed=False in YouTube DB so it can be retried on next run!

        # Respectful pause to stay well within rate limits
        if idx % batch_size == 0:
            print(f"⏳ Completed batch of {batch_size}. Pausing {pause_sec * 2}s...")
            time.sleep(pause_sec * 2)
        else:
            time.sleep(pause_sec)

    # 4. Complete pipeline run
    status = 'completed' if failed_count == 0 else 'failed'
    db.complete_run(run_id, status, len(viable_candidates), processed_count, 0, failed_count)

    print("\n" + "=" * 60)
    print(f"🎉 Catch-up Ingestion Finished!")
    print(f"   • Total Viable: {len(viable_candidates)}")
    print(f"   • Successfully Ingested: {processed_count}")
    print(f"   • Failed: {failed_count}")
    print("=" * 60)

    # 5. Rebuild wiki index and Quartz site if changes occurred
    if processed_count > 0:
        print("\n📚 Rebuilding Wiki index and index.md...")
        try:
            subprocess.run([sys.executable, str(PROJECT_DIR / "scripts" / "indexer.py")], check=True)
            subprocess.run([sys.executable, str(PROJECT_DIR / "scripts" / "rebuild_index_md.py")], check=True)
            print("✅ Wiki indices successfully rebuilt.")
            
            # Final unified sync to GitHub & Vercel
            subprocess.run(["git", "add", "wiki/", "wiki_index.json"], check=False)
            diff_res = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
            if diff_res.returncode != 0:
                subprocess.run(["git", "commit", "-m", f"feat(youtube): batch catchup ingested {processed_count} videos"], check=False)
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("🚀 Successfully pushed all catch-up updates to GitHub & Vercel.")
        except Exception as e:
            print(f"⚠️ Final sync notice: {e}")

if __name__ == "__main__":
    run_catchup()
