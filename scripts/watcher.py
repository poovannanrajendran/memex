import os
import time
import subprocess
import sys
import json as _json
from db import db
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = "raw"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_MINUTES", 15)) * 60

def get_source_type(file_path):
    path_lower = file_path.lower()
    ext = os.path.splitext(path_lower)[1]
    
    if "raw/articles/" in path_lower and ext in ['.md', '.txt', '.html']:
        return "article"
    elif "raw/pdfs/" in path_lower and ext == '.pdf':
        return "pdf"
    elif "raw/transcripts/" in path_lower and ext in ['.md', '.txt']:
        return "transcript"
    elif "raw/youtube/" in path_lower and ext in ['.json', '.md']:
        return "youtube"
    elif "raw/posts/" in path_lower and ext == '.md':
        return "post"
    else:
        return "unknown"

def run_ingest(run_id, file_id, file_path):
    """Executes ingestion for a single file with fallback logic."""
    print(f"Starting ingestion for: {file_path}")
    step_id = db.start_step(run_id, 'ingest', file_id)
    
    primary_model = os.getenv("GEMINI_INGEST_MODEL", "gemini-2.5-flash-lite")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
    
    try:
        # Try primary model
        cmd = ["python3", "scripts/ingest.py", file_path, str(run_id), str(file_id), primary_model]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if "RESOURCE_EXHAUSTED" in result.stderr or "429" in result.stderr:
                print(f"Primary model {primary_model} exhausted. Retrying with fallback {fallback_model}...")
                cmd[-1] = fallback_model
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Ingestion failed for {file_path}: {result.stderr}")
                db.complete_step(step_id, 'failed', error_message=result.stderr)
                return False

        print(result.stdout)
        db.complete_step(step_id, 'completed', output_summary=f"Ingested {file_path}")
        return True
        
    except Exception as e:
        print(f"Exception during ingestion of {file_path}: {e}")
        db.complete_step(step_id, 'failed', error_message=str(e))
        return False

def notify_openclaw(run_id: str, processed_files: list):
    """Post newly ingested wiki pages to n8n for Qdrant sync."""
    n8n_url = os.getenv("N8N_MEMEX_SYNC_URL", "")
    if not n8n_url or not processed_files:
        return

    # Load wiki_index to get metadata for processed files
    wiki_index_path = "wiki_index.json"
    if not os.path.exists(wiki_index_path):
        return

    try:
        with open(wiki_index_path) as f:
            index = _json.load(f)
    except Exception as e:
        print(f"[openclaw notify] Failed to load index: {e}")
        return

    import requests as _req
    for fpath in processed_files:
        # Derive slug from file path: wiki/sources/foo.md → "foo"
        slug = os.path.splitext(os.path.basename(fpath))[0]
        entry_type = None
        entry = None
        for t in ["sources", "entities", "concepts", "synthesis"]:
            if slug in index.get(t, {}):
                entry_type = t
                entry = index[t][slug]
                break
        if not entry_type:
            continue
        try:
            _req.post(n8n_url, json={
                "event": "memex_ingested",
                "run_id": str(run_id),
                "type": entry_type,
                "slug": slug,
                "title": entry.get("title", slug),
                "summary": (entry.get("summary") or "")[:400],
                "file_path": entry.get("file_path", fpath),
                "trigger_source": "openclaw"
            }, timeout=5)
        except Exception as e:
            print(f"[openclaw notify] {slug}: {e}")

def watch():
    print("--- Starting memex Automation Run ---")
    
    # 1. Sync with GitHub first to ensure we have the latest wiki state
    try:
        subprocess.run(["git", "pull", "origin", "main", "--no-rebase"], check=True)
    except Exception as e:
        print(f"Git pull failed: {e}")

    files_to_process = []
    for root, dirs, files in os.walk(RAW_DIR):
        if "assets" in root: continue
        if "youtube_tmp" in root: continue
        for f in files:
            if f.startswith('.') or f.endswith('.csv'): continue # skip CSVs and hidden files
            fpath = os.path.join(root, f)
            files_to_process.append(fpath)

    if not files_to_process:
        print("No files found in raw/.")
        return

    # Create the run record
    run_id = db.create_run(triggered_by='watcher')
    
    work_queue = []
    for fpath in files_to_process:
        s_type = get_source_type(fpath)
        file_id = db.register_file(run_id, fpath, s_type)
        if file_id:
            work_queue.append((file_id, fpath))

    if not work_queue:
        print("No new files to process.")
        db.complete_run(run_id, 'no_work', len(files_to_process), 0, len(files_to_process), 0)
        return

    print(f"Found {len(work_queue)} new files. Starting run {run_id}")
    
    processed = 0
    failed = 0
    processed_paths = []
    
    # 1. BATCH INGEST
    for file_id, fpath in work_queue:
        if run_ingest(run_id, file_id, fpath):
            processed += 1
            processed_paths.append(fpath)
        else:
            failed += 1

    if processed > 0:
        # 2. BATCH LINT (Run once after all ingests)
        print("Running batch lint...")
        step_id = db.start_step(run_id, 'lint')
        try:
            subprocess.run(["python3", "scripts/lint.py", str(run_id)], check=True)
            db.complete_step(step_id, 'completed')
        except Exception as e:
            db.complete_step(step_id, 'failed', error_message=str(e))

        # 3. BATCH SYNTHESIS (Run once after all ingests)
        print("Running batch synthesis...")
        step_id = db.start_step(run_id, 'synthesise')
        try:
            topic = "Lloyd's and AI recent updates"
            subprocess.run(["python3", "scripts/synthesise.py", topic, str(run_id)], check=True)
            db.complete_step(step_id, 'completed', output_summary=f"Synthesised topic: {topic}")
        except Exception as e:
            db.complete_step(step_id, 'failed', error_message=str(e))

        # 4. FINAL PUSH & PROBE (Trigger Vercel)
        print("Pushing final state to GitHub...")
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Successfully synced. Probing Vercel deployment...")
            subprocess.run(["python3", "scripts/probe_vercel.py"], check=True)
            # Notify OpenClaw of new pages
            notify_openclaw(run_id, processed_paths)
        except Exception as e:
            print(f"Post-ingest sync/probe failed: {e}")

    db.write_ai_summary(run_id)
    db.complete_run(run_id, 'completed', len(files_to_process), processed, 0, failed)
    print(f"Run {run_id} completed. Processed: {processed}, Failed: {failed}")

if __name__ == "__main__":
    watch()
