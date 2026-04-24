import os
import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# Database Connection for YouTube Liked Videos
YOUTUBE_DB_URL = "postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos"

def is_usable_content(text):
    if not text:
        return False
    # Strip hashtags and links to see if real text remains
    clean_text = re.sub(r'#\w+', '', text)
    clean_text = re.sub(r'http\S+', '', clean_text)
    clean_text = clean_text.strip()
    
    # Require at least 100 chars of actual prose
    return len(clean_text) > 100

def get_unprocessed_videos(limit=50):
    conn = psycopg2.connect(YOUTUBE_DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get unprocessed videos that have EITHER a transcript OR a description
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

def mark_as_processed(video_id):
    conn = psycopg2.connect(YOUTUBE_DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s", (video_id,))
        conn.commit()
    finally:
        conn.close()

def process_delta(limit=50):
    print(f"Checking for new YouTube delta records (limit {limit})...")
    
    # Sync with GitHub first to capture any manual GUI deletions/edits
    try:
        subprocess.run(["git", "pull", "origin", "main", "--no-rebase"], check=True)
    except Exception as e:
        print(f"Initial git pull failed (normal if first run): {e}")

    videos = get_unprocessed_videos(limit)
    
    if not videos:
        print("No new videos to process.")
        return

    print(f"Found {len(videos)} candidate videos.")
    
    temp_dir = "raw/youtube_tmp"
    os.makedirs(temp_dir, exist_ok=True)

    processed_this_batch = 0
    for video in videos:
        title = video['title']
        v_id = video['video_id']
        
        transcript = video.get('transcript')
        description = video.get('description')
        
        content_body = ""
        if transcript and transcript != 'No transcript available' and len(transcript) > 50:
            content_body = f"Transcript:\n{transcript}"
        elif is_usable_content(description):
            content_body = f"Description (Fallback):\n{description}"
        
        if not content_body:
            print(f"Skipping {v_id}: No usable content (description too short or just hashtags/links).")
            # We still mark as processed so we don't keep picking it up
            mark_as_processed(v_id)
            continue

        content = f"Title: {title}\nURL: {video['youtube_url']}\n\n{content_body}"
        
        # Write to temp file
        safe_title = "".join([c if c.isalnum() else "_" for c in title])
        file_path = os.path.join(temp_dir, f"{v_id}_{safe_title[:50]}.txt")
        
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)
        
        print(f"Ingesting: {title}...")
        try:
            subprocess.run([sys.executable, "scripts/ingest.py", file_path, "0", "0", "gemini-2.5-flash-lite"], check=True)
            mark_as_processed(v_id)
            print(f"Successfully processed {v_id}")
            os.remove(file_path)
            processed_this_batch += 1
        except Exception as e:
            print(f"Failed to process {v_id}: {e}")

    print(f"Batch complete. Processed {processed_this_batch} videos.")
    
    if processed_this_batch > 0:
        print("Pushing changes to GitHub...")
        try:
            # We push to the current branch. On server it is 'master'
            # Using -u set-upstream once if needed, but simple push should work
            subprocess.run(["git", "push", "origin", "HEAD"], check=True)
            print("Successfully synced with GitHub.")
        except Exception as e:
            print(f"Git push failed: {e}")

if __name__ == "__main__":
    limit = 50
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            limit = 2000
        else:
            limit = int(sys.argv[1])
            
    process_delta(limit)
