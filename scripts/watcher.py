import os
import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# Database Connection for YouTube Liked Videos and Manual Inbox
DB_URL = "postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos"

def is_usable_content(text):
    if not text:
        return False
    # Strip hashtags and links to see if real text remains
    clean_text = re.sub(r'#\w+', '', text)
    clean_text = re.sub(r'http\S+', '', clean_text)
    clean_text = clean_text.strip()
    return len(clean_text) > 100

def get_unprocessed_youtube(limit=5):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT video_id, title, transcript, description, youtube_url 
                   FROM youtube_videos 
                   WHERE isprocessed = false 
                   AND (
                       (transcript IS NOT NULL AND transcript != 'No transcript available' AND length(transcript) > 50)
                       OR 
                       (description IS NOT NULL AND length(description) > 150)
                   )
                   LIMIT %s""",
                (limit,)
            )
            return cur.fetchall()
    finally:
        conn.close()

def get_unprocessed_inbox(limit=10):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, content, source_url FROM memex_inbox WHERE is_processed = false LIMIT %s",
                (limit,)
            )
            return cur.fetchall()
    finally:
        conn.close()

def mark_youtube_processed(video_id):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s", (video_id,))
        conn.commit()
    finally:
        conn.close()

def mark_inbox_processed(item_id):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE memex_inbox SET is_processed = true WHERE id = %s", (item_id,))
        conn.commit()
    finally:
        conn.close()

def run_watcher(yt_limit=5, inbox_limit=10):
    print("--- Starting Second Brain Watcher ---")
    
    # 1. Pull latest from GitHub (capture manual deletions/edits)
    try:
        print("Syncing with GitHub (Pull)...")
        subprocess.run(["git", "pull", "origin", "main", "--no-rebase"], check=True)
    except Exception as e:
        print(f"Git pull warning: {e}")

    temp_dir = "raw/youtube_tmp"
    os.makedirs(temp_dir, exist_ok=True)
    total_processed = 0

    # 2. Process YouTube Delta
    print(f"Checking YouTube delta (limit {yt_limit})...")
    videos = get_unprocessed_youtube(yt_limit)
    for video in videos:
        title = video['title']
        v_id = video['video_id']
        content_body = ""
        
        if video.get('transcript') and video['transcript'] != 'No transcript available' and len(video['transcript']) > 50:
            content_body = f"Transcript:\n{video['transcript']}"
        elif is_usable_content(video.get('description')):
            content_body = f"Description (Fallback):\n{video['description']}"
        
        if not content_body:
            mark_youtube_processed(v_id)
            continue

        file_path = os.path.join(temp_dir, f"yt_{v_id}.txt")
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(f"Title: {title}\nURL: {video['youtube_url']}\n\n{content_body}")
        
        try:
            subprocess.run([sys.executable, "scripts/ingest.py", file_path, "0", "0", "gemini-2.5-flash-lite"], check=True)
            mark_youtube_processed(v_id)
            os.remove(file_path)
            total_processed += 1
        except Exception as e:
            print(f"Failed YouTube ingest {v_id}: {e}")

    # 3. Process Manual Inbox Delta
    print(f"Checking Manual Inbox delta (limit {inbox_limit})...")
    items = get_unprocessed_inbox(inbox_limit)
    for item in items:
        title = item['title'] or "Inbox Note"
        item_id = item['id']
        file_path = os.path.join(temp_dir, f"inbox_{item_id}.txt")
        
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(f"Title: {title}\nSource: {item['source_url'] or 'Manual Entry'}\n\nContent:\n{item['content']}")
        
        try:
            # We use gemini-2.5-flash-lite for manual notes too
            subprocess.run([sys.executable, "scripts/ingest.py", file_path, "0", "0", "gemini-2.5-flash-lite"], check=True)
            mark_inbox_processed(item_id)
            os.remove(file_path)
            total_processed += 1
        except Exception as e:
            print(f"Failed Inbox ingest {item_id}: {e}")

    # 4. Push final state to GitHub
    if total_processed > 0:
        print(f"Processed {total_processed} items. Syncing with GitHub (Push)...")
        try:
            subprocess.run(["git", "push", "origin", "HEAD"], check=True)
            print("Successfully synced.")
        except Exception as e:
            print(f"Git push failed: {e}")
    else:
        print("No new content to process.")

if __name__ == "__main__":
    run_watcher()
