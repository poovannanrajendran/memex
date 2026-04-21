import os
import time
import subprocess
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

def run_pipeline(run_id, file_id, file_path):
    """Executes the full pipeline for a single file."""
    print(f"Starting pipeline for: {file_path}")
    
    # 1. Ingest
    step_id = db.start_step(run_id, 'ingest', file_id)
    try:
        # Pass run_id and file_id to ingest.py (needs to be updated to accept them)
        subprocess.run(["python3", "scripts/ingest.py", file_path, str(run_id), str(file_id)], check=True)
        db.complete_step(step_id, 'completed', output_summary=f"Ingested {file_path}")
    except Exception as e:
        db.complete_step(step_id, 'failed', error_message=str(e))
        raise e

    # 2. Lint (Global)
    step_id = db.start_step(run_id, 'lint')
    try:
        subprocess.run(["python3", "scripts/lint.py", str(run_id)], check=True)
        db.complete_step(step_id, 'completed')
    except Exception as e:
        db.complete_step(step_id, 'failed', error_message=str(e))

    # 3. Synthesise (Topic-based, here we use a general refresh)
    step_id = db.start_step(run_id, 'synthesise')
    try:
        # Example topic
        subprocess.run(["python3", "scripts/synthesise.py", "Lloyd's and AI recent updates", str(run_id)], check=True)
        db.complete_step(step_id, 'completed')
    except Exception as e:
        db.complete_step(step_id, 'failed', error_message=str(e))

def watch():
    print("Watcher started...")
    
    # Pre-scan to find work
    files_to_process = []
    for root, dirs, files in os.walk(RAW_DIR):
        if "assets" in root: continue
        for f in files:
            if f.startswith('.'): continue
            fpath = os.path.join(root, f)
            # Try to register - if it works, it's new
            # We use a dummy UUID temporarily to check for existence via register_file
            files_to_process.append(fpath)

    if not files_to_process:
        print("No files found in raw/. Checking for unprocessed...")
        # Since register_file handles deduplication, we actually need to create the run first
        # to get a valid UUID for the foreign key.
        
    # Create the run
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
    
    for file_id, fpath in work_queue:
        try:
            run_pipeline(run_id, file_id, fpath)
            processed += 1
        except Exception as e:
            print(f"Pipeline failed for {fpath}: {e}")
            failed += 1
            
    db.write_ai_summary(run_id)
    db.complete_run(run_id, 'completed', len(files_to_process), processed, 0, failed)
    print(f"Run {run_id} completed. Processed: {processed}, Failed: {failed}")

if __name__ == "__main__":
    watch()
