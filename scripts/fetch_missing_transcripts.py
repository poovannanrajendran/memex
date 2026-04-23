import os
import psycopg2
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_DB_URL = "postgresql://dbuser:dbuser@192.168.1.20:5432/youtube_liked_videos"

def get_videos_missing_transcripts():
    conn = psycopg2.connect(YOUTUBE_DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT video_id, title FROM youtube_videos WHERE transcript IS NULL OR transcript = 'No transcript available' OR length(transcript) < 50 LIMIT 100"
            )
            return cur.fetchall()
    finally:
        conn.close()

def update_transcript(video_id, transcript):
    conn = psycopg2.connect(YOUTUBE_DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE youtube_videos SET transcript = %s WHERE video_id = %s",
                (transcript, video_id)
            )
        conn.commit()
    finally:
        conn.close()

def run_fix():
    videos = get_videos_missing_transcripts()
    print(f"Attempting to recover {len(videos)} transcripts...")
    
    success_count = 0
    fail_count = 0
    for v_id, title in videos:
        print(f"[{v_id}] {title[:40]}...", end=" ")
        try:
            # TRY METHOD 1: get_transcript
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(v_id, languages=['en', 'ta'])
            except:
                # TRY METHOD 2: list_transcripts then pick any
                transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                transcript_data = next(iter(transcript_list)).fetch()

            full_text = " ".join([t['text'] for t in transcript_data])
            
            if len(full_text) > 50:
                update_transcript(v_id, full_text)
                print("✅")
                success_count += 1
            else:
                print("⚠️ short")
                fail_count += 1
        except Exception as e:
            err_msg = str(e).split('\n')[0]
            print(f"❌ {err_msg[:50]}")
            fail_count += 1
            
    print(f"\nDone. Recovered {success_count} transcripts. Failed: {fail_count}")

if __name__ == "__main__":
    run_fix()
