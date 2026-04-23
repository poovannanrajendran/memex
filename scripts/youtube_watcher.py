import os
import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

# Database Connection for YouTube Liked Videos
# postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos
YOUTUBE_DB_URL = "postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos"

def get_unprocessed_videos(limit=10):
    conn = psycopg2.connect(YOUTUBE_DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT video_id, title, transcript, youtube_url FROM youtube_videos WHERE isprocessed = false AND transcript IS NOT NULL AND transcript != 'No transcript available' LIMIT %s",
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

def process_delta(limit=10):
    print(f"Checking for new YouTube delta records (limit {limit})...")
    videos = get_unprocessed_videos(limit)
    
    if not videos:
        print("No new videos to process.")
        return

    print(f"Found {len(videos)} new videos.")
    
    # Create a temporary directory for ingestion if it doesn't exist
    temp_dir = "raw/youtube_tmp"
    os.makedirs(temp_dir, exist_ok=True)

    for video in videos:
        title = video['title']
        v_id = video['video_id']
        content = f"Title: {title}\nURL: {video['youtube_url']}\n\nTranscript:\n{video['transcript']}"
        
        # Write to temp file
        safe_title = "".join([c if c.isalnum() else "_" for c in title])
        file_path = os.path.join(temp_dir, f"{v_id}_{safe_title[:50]}.txt")
        
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)
        
        print(f"Ingesting: {title}...")
        try:
            # Call the ingestion script
            # We use gemini-2.5-flash-lite for cost efficiency as requested for bulk
            subprocess.run(["python", "scripts/ingest.py", file_path, "0", "0", "gemini-2.5-flash-lite"], check=True)
            
            # Mark as processed in PG
            mark_as_processed(v_id)
            print(f"Successfully processed {v_id}")
            
            # Clean up temp file
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to process {v_id}: {e}")

    print("Batch complete.")

if __name__ == "__main__":
    # If run with 'all' or a number, change limit
    limit = 10
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            limit = 1000
        else:
            limit = int(sys.argv[1])
            
    process_delta(limit)
