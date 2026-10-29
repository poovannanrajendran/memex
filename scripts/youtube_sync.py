import os
import re
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEFAULT_YOUTUBE_DB_URL = "postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos"

def is_usable_content(text: str) -> bool:
    """
    Checks if the given text has substantive content rather than
    just hashtags, links, or short phrases.
    Requires at least 100 characters of clean prose.
    """
    if not text:
        return False
    # Strip hashtags, URLs, and extra whitespace
    clean_text = re.sub(r'#\w+', '', text)
    clean_text = re.sub(r'https?://\S+', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return len(clean_text) >= 100

def format_video_markdown(video: dict) -> str:
    """
    Converts a database video row into a canonical Memex raw YouTube record.
    Matches the schema expected by scripts/ingest.py and the Karpathy wiki pattern.
    """
    title = (video.get("title") or "Untitled Video").replace('"', '\\"')
    url = video.get("youtube_url") or f"https://www.youtube.com/watch?v={video.get('video_id', '')}"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    tags = video.get("tags") or ""
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tag_list = tags
    else:
        tag_list = []
    
    if "youtube" not in tag_list:
        tag_list.insert(0, "youtube")

    transcript = video.get("transcript")
    description = video.get("description")
    
    body = ""
    if transcript and transcript != "No transcript available" and len(transcript.strip()) > 50:
        body = f"## Transcript\n\n{transcript.strip()}"
    elif description and is_usable_content(description):
        body = f"## Description\n\n{description.strip()}"
    else:
        body = "## Content\n\nNo substantive transcript or description available."

    md = f"""---
title: "{title}"
source_type: youtube
url: "{url}"
ingested: {date_str}
confidence: medium
tags: {tag_list}
---

{body}
"""
    return md

class YouTubeSyncManager:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("YOUTUBE_DB_URL", DEFAULT_YOUTUBE_DB_URL)
        self.conn = None

    def _get_connection(self, retries: int = 3, delay: float = 1.0):
        """Establishes or reconnects to PostgreSQL with retry backoff."""
        if self.conn and not self.conn.closed:
            # Check connection with a probe
            try:
                with self.conn.cursor() as probe_cur:
                    probe_cur.execute("SELECT 1;")
                return self.conn
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                try:
                    self.conn.close()
                except Exception:
                    pass
                self.conn = None

        for attempt in range(1, retries + 1):
            try:
                self.conn = psycopg2.connect(self.db_url)
                self.conn.autocommit = True
                return self.conn
            except Exception as e:
                if attempt == retries:
                    raise
                time.sleep(delay * attempt)

    def fetch_unprocessed(self, limit: int = None) -> list:
        """Fetches all unprocessed videos from the database."""
        try:
            conn = self._get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM youtube_videos WHERE isprocessed = false ORDER BY added_at ASC"
                if limit:
                    query += f" LIMIT {int(limit)}"
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            # Try one recovery cycle
            conn = self._get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM youtube_videos WHERE isprocessed = false ORDER BY added_at ASC"
                if limit:
                    query += f" LIMIT {int(limit)}"
                cur.execute(query)
                return cur.fetchall()

    def mark_processed(self, video_id: str):
        """Marks a video as processed in the database."""
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s",
                (video_id,)
            )

    def sync_batch(self, limit: int = None, ingest_fn = None, output_dir: str = "raw/youtube") -> dict:
        """
        Processes pending videos:
        - Non-viable videos are marked processed immediately to unblock queue.
        - Usable videos are formatted to markdown and passed to ingest_fn.
        - Only videos that pass ingest_fn successfully are marked processed.
        - If server terminates or network disconnects, unprocessed or failed items remain isprocessed=false.
        """
        os.makedirs(output_dir, exist_ok=True)
        videos = self.fetch_unprocessed(limit=limit)
        
        stats = {
            "total_found": len(videos),
            "processed": 0,
            "skipped": 0,
            "failed": 0
        }
        
        for video in videos:
            v_id = video.get("video_id")
            title = video.get("title", "Untitled")
            transcript = video.get("transcript")
            description = video.get("description")
            
            has_transcript = bool(transcript and transcript != "No transcript available" and len(transcript.strip()) > 50)
            has_desc = bool(description and is_usable_content(description))
            
            if not has_transcript and not has_desc:
                # Non-viable video (shorts/music with no text)
                self.mark_processed(v_id)
                stats["skipped"] += 1
                continue
                
            # Valid candidate for ingestion
            md_content = format_video_markdown(video)
            safe_title = "".join([c if c.isalnum() else "_" for c in title])[:40].strip("_")
            file_path = os.path.join(output_dir, f"{v_id}_{safe_title}.md")
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                success = False
                if ingest_fn:
                    success = ingest_fn(file_path)
                else:
                    success = True
                    
                if success:
                    self.mark_processed(v_id)
                    stats["processed"] += 1
                else:
                    stats["failed"] += 1
                    # Clean up file so watcher doesn't duplicate before next retry
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass
            except Exception as e:
                stats["failed"] += 1
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                        
        return stats

    def stage_unprocessed(self, limit: int = None, output_dir: str = "raw/youtube") -> list:
        """
        Fetches unprocessed videos from the database:
        - Automatically marks non-viable records as processed (to prevent queue congestion).
        - Writes candidate viable videos to output_dir (e.g. raw/youtube/{video_id}_{title}.md).
        - Returns a list of staged (video_id, file_path) tuples.
        - Does NOT mark viable videos as processed yet (they are marked only after run_ingest succeeds).
        """
        os.makedirs(output_dir, exist_ok=True)
        videos = self.fetch_unprocessed(limit=limit)
        staged_files = []
        
        for video in videos:
            v_id = video.get("video_id")
            title = video.get("title", "Untitled")
            transcript = video.get("transcript")
            description = video.get("description")
            
            has_transcript = bool(transcript and transcript != "No transcript available" and len(transcript.strip()) > 50)
            has_desc = bool(description and is_usable_content(description))
            
            if not has_transcript and not has_desc:
                # Non-viable video (shorts/music with no text)
                self.mark_processed(v_id)
                continue
                
            safe_title = "".join([c if c.isalnum() else "_" for c in title])[:40].strip("_")
            file_path = os.path.join(output_dir, f"{v_id}_{safe_title}.md")
            
            if not os.path.exists(file_path):
                md_content = format_video_markdown(video)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                    
            staged_files.append((v_id, file_path))
            
        return staged_files

# Helper aliases
def fetch_unprocessed_videos(limit=None, db_url=None):
    mgr = YouTubeSyncManager(db_url=db_url)
    return mgr.fetch_unprocessed(limit=limit)

def mark_video_processed(video_id, db_url=None):
    mgr = YouTubeSyncManager(db_url=db_url)
    mgr.mark_processed(video_id)

def stage_unprocessed_videos(limit=None, db_url=None, output_dir="raw/youtube"):
    mgr = YouTubeSyncManager(db_url=db_url)
    return mgr.stage_unprocessed(limit=limit, output_dir=output_dir)

def sync_youtube_liked_videos(limit=None, ingest_fn=None, db_url=None, output_dir="raw/youtube"):
    mgr = YouTubeSyncManager(db_url=db_url)
    return mgr.sync_batch(limit=limit, ingest_fn=ingest_fn, output_dir=output_dir)
