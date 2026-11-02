import os
import time
import subprocess
import sys
import json as _json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.db import db
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

def is_spend_cap_error(err_str: str) -> bool:
    """Checks if error represents a project-level monthly spending cap exhaustion."""
    err_lower = err_str.lower()
    return "spending cap" in err_lower or "spend cap" in err_lower

def run_ingest(run_id, file_id, file_path):
    """Executes ingestion for a single file with fallback logic."""
    print(f"Starting ingestion for: {file_path}")
    step_id = db.start_step(run_id, 'ingest', file_id)
    
    primary_model = os.getenv("GEMINI_INGEST_MODEL", "gemini-2.5-flash-lite")
    fallback_model = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
    
    try:
        # Try primary model with --batch flag since watcher already holds pipeline lock
        cmd = [sys.executable, "scripts/ingest.py", file_path, str(run_id), str(file_id), primary_model, "--batch"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Circuit breaker: Never fallback if the project spend cap is hit
            if is_spend_cap_error(result.stderr):
                print(f"CRITICAL: Project spend cap reached during {file_path}. Aborting model retries.")
                db.complete_step(step_id, 'failed', error_message="Project monthly spend cap exceeded.")
                return "SPEND_CAP_EXCEEDED"

            if "RESOURCE_EXHAUSTED" in result.stderr or "429" in result.stderr:
                print(f"Primary model {primary_model} rate limited. Retrying with fallback {fallback_model}...")
                cmd[5] = fallback_model
                result = subprocess.run(cmd, capture_output=True, text=True)
                if is_spend_cap_error(result.stderr):
                    print("CRITICAL: Project spend cap reached on fallback. Aborting.")
                    db.complete_step(step_id, 'failed', error_message="Project monthly spend cap exceeded.")
                    return "SPEND_CAP_EXCEEDED"
            
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
    from scripts.delivery import enqueue_source, drain_outbox
    errors = []
    for file_path in processed_files:
        try:
            enqueue_source(db, run_id, file_path)
        except Exception as exc:
            errors.append(str(exc))
    result = drain_outbox(db)
    if errors or result["failed"] or result["pending"]:
        raise RuntimeError("Qdrant delivery incomplete; durable outbox will retry. " + "; ".join(errors))
    return result


def watch():
    print("--- Starting memex Automation Run ---")
    db.validate_schema()
    
    # 1. Sync with GitHub first to ensure we have the latest wiki state
    try:
        subprocess.run(["git", "pull", "origin", "main", "--no-rebase"], check=True)
    except Exception as e:
        print(f"Git pull failed: {e}")

    # 2. Stage pending YouTube liked videos into raw/youtube/
    try:
        from youtube_sync import stage_unprocessed_videos, mark_video_processed
        staged = stage_unprocessed_videos(output_dir="raw/youtube")
        if staged:
            print(f"Staged {len(staged)} candidate YouTube videos for ingestion.")
    except Exception as e:
        print(f"Warning: YouTube liked videos sync failed: {e}")

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
    skipped_count = 0
    try:
        for fpath in files_to_process:
            s_type = get_source_type(fpath)
            file_id = db.register_file(run_id, fpath, s_type, reingest_if_completed=False)
            if file_id is not None:
                work_queue.append((file_id, fpath))
            else:
                skipped_count += 1
    except Exception as exc:
        db.complete_run(run_id, 'failed', len(files_to_process), 0, skipped_count, 1,
                        error_message=str(exc))
        raise

    if not work_queue:
        print(f"All {len(files_to_process)} files in raw/ are already ingested and up to date.")
        try:
            notify_openclaw(run_id, files_to_process)
        except Exception as exc:
            db.complete_run(run_id, 'failed', len(files_to_process), 0, skipped_count, 1,
                            error_message=str(exc))
            raise
        db.complete_run(run_id, 'completed', len(files_to_process), 0, skipped_count, 0)
        return

    print(f"Found {len(work_queue)} new/modified files ({skipped_count} already completed). Starting run {run_id}")
    
    processed = 0
    failed = 0
    processed_paths = []
    
    # 1. BATCH INGEST
    spend_cap_tripped = False
    errors = []
    for file_id, fpath in work_queue:
        ingest_res = run_ingest(run_id, file_id, fpath)
        if ingest_res is True:
            processed += 1
            processed_paths.append(fpath)
            # If this is a YouTube video, mark as processed in the YouTube staging DB
            if "raw/youtube/" in fpath:
                try:
                    from youtube_sync import mark_video_processed
                    v_id = os.path.basename(fpath).split('_')[0]
                    mark_video_processed(v_id)
                except Exception as e:
                    print(f"Warning: Failed to mark {v_id} as processed in YouTube DB: {e}")
        elif ingest_res == "SPEND_CAP_EXCEEDED":
            failed += 1
            spend_cap_tripped = True
            print("Circuit breaker triggered: Halting remaining queue due to spend cap.")
            break
        else:
            failed += 1

    if spend_cap_tripped:
        # Spending cap hit: Immediately abort any downstream LLM calls (synthesis, etc.)
        print("Spend cap exceeded during batch: Skipping lint and synthesis to prevent further charges.")
        # Still index and commit what succeeded so far
        if processed > 0:
            try:
                from indexer import build_wiki_index
                build_wiki_index()
                from rebuild_index_md import rebuild_index
                rebuild_index()
                subprocess.run(["git", "add", "wiki/", "wiki_index.json"], check=True)
                subprocess.run(["git", "commit", "-m", f"ingest(partial): {processed} source(s) before spend cap trip in run {run_id}"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
            except Exception as e:
                print(f"Warning: Partial commit/push failed: {e}")
        db.complete_run(run_id, 'failed', len(work_queue), processed, skipped_count, failed, error_message="Run aborted: Project monthly spend cap reached.")
        return

    if processed > 0:
        # Rebuild wiki index first so batch lint and batch synthesis have full access to newly ingested pages
        print("Rebuilding wiki index for newly ingested sources...")
        try:
            from indexer import build_wiki_index
            build_wiki_index()
            from rebuild_index_md import rebuild_index
            rebuild_index()
        except Exception as e:
            errors.append(f"Preliminary index: {e}")
            db.complete_run(run_id, 'failed', len(files_to_process), processed, skipped_count, failed,
                            error_message="; ".join(errors))
            raise

        # 2. BATCH LINT (Run once after all ingests)
        print("Running batch lint...")
        step_id = db.start_step(run_id, 'lint')
        try:
            subprocess.run([sys.executable, "scripts/lint.py", str(run_id)], check=True)
            db.complete_step(step_id, 'completed')
        except Exception as e:
            db.complete_step(step_id, 'failed', error_message=str(e))
            errors.append(str(e))

        # 3. BATCH SYNTHESIS (Run once after all ingests)
        print("Running batch synthesis...")
        step_id = db.start_step(run_id, 'synthesise')
        try:
            topic = "Lloyd's and AI recent updates"
            subprocess.run([sys.executable, "scripts/synthesise.py", topic, str(run_id)], check=True)
            db.complete_step(step_id, 'completed', output_summary=f"Synthesised topic: {topic}")
        except Exception as e:
            db.complete_step(step_id, 'failed', error_message=str(e))
            errors.append(str(e))

        # Re-index to ensure synthesis output is also included in wiki_index.json
        try:
            from indexer import build_wiki_index
            build_wiki_index()
            from rebuild_index_md import rebuild_index
            rebuild_index()
        except Exception as e:
            errors.append(f"Final index: {e}")

        # Commit batch changes
        try:
            subprocess.run(["git", "add", "wiki/", "wiki_index.json"], check=True)
            subprocess.run(["git", "commit", "-m", f"ingest(batch): {processed} source(s) processed in run {run_id}"], check=True)
        except Exception as e:
            errors.append(f"Git commit: {e}")

        # 4. FINAL PUSH & PROBE (Trigger Vercel)
        print("Pushing final state to GitHub...")
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Successfully synced. Probing Vercel deployment...")
            subprocess.run([sys.executable, "scripts/probe_vercel.py"], check=True)
        except Exception as e:
            errors.append(f"Push or probe: {e}")
        try:
            notify_openclaw(run_id, processed_paths)
        except Exception as e:
            errors.append(f"Delivery: {e}")

    db.write_ai_summary(run_id)
    db.complete_run(run_id, 'failed' if failed or errors else 'completed', len(files_to_process),
                    processed, skipped_count, failed, error_message="; ".join(errors) or None)
    print(f"Run {run_id} completed. Processed: {processed}, Failed: {failed}")

if __name__ == "__main__":
    from lock import pipeline_lock, LockAcquisitionError
    try:
        with pipeline_lock(blocking=False):
            watch()
    except LockAcquisitionError as e:
        print(f"Skipping run: {e}")
