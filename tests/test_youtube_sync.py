import unittest
from unittest.mock import MagicMock, patch
import os
import psycopg2

# We import the module under test (will fail or be tested)
from scripts.youtube_sync import (
    is_usable_content,
    format_video_markdown,
    fetch_unprocessed_videos,
    mark_video_processed,
    sync_youtube_liked_videos,
    YouTubeSyncManager,
)

class TestYouTubeSync(unittest.TestCase):

    def test_is_usable_content_positive(self):
        # Substantive text over 100 chars
        text = "This is a comprehensive guide on building autonomous AI agents with Python, LLMs, and memory systems for production workloads."
        self.assertTrue(is_usable_content(text))

    def test_is_usable_content_negative_empty_and_short(self):
        self.assertFalse(is_usable_content(""))
        self.assertFalse(is_usable_content(None))
        self.assertFalse(is_usable_content("Short text"))

    def test_is_usable_content_negative_hashtags_and_urls(self):
        # Long string but made entirely of hashtags and links
        text = "#ai #coding #python #tech #agent #llm #dev #news #software https://youtube.com/watch?v=123 https://poovi.me #test #build"
        self.assertFalse(is_usable_content(text))

    def test_format_video_markdown_with_transcript(self):
        video = {
            "video_id": "test1234",
            "title": "Building Autonomous Agents",
            "youtube_url": "https://www.youtube.com/watch?v=test1234",
            "transcript": "In this video, we explore the Karpathy LLM Wiki pattern and agent memory.",
            "description": "Short description",
            "tags": "ai,agents,memex"
        }
        md = format_video_markdown(video)
        self.assertIn("title: \"Building Autonomous Agents\"", md)
        self.assertIn("source_type: youtube", md)
        self.assertIn("https://www.youtube.com/watch?v=test1234", md)
        self.assertIn("## Transcript", md)
        self.assertIn("In this video, we explore the Karpathy LLM Wiki pattern", md)

    def test_format_video_markdown_with_description_fallback(self):
        desc = "This is a detailed video description explaining how to optimize vector databases with Qdrant and embeddings." * 2
        video = {
            "video_id": "test5678",
            "title": "Vector Databases 101",
            "youtube_url": "https://www.youtube.com/watch?v=test5678",
            "transcript": "No transcript available",
            "description": desc,
            "tags": "vector,qdrant"
        }
        md = format_video_markdown(video)
        self.assertIn("title: \"Vector Databases 101\"", md)
        self.assertIn("## Description", md)
        self.assertIn(desc, md)

    def test_sync_successful_ingestion(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        video = {
            "video_id": "vid001",
            "title": "Agentic AI in Insurance",
            "youtube_url": "https://youtube.com/watch?v=vid001",
            "transcript": "A detailed discussion on Lloyd's market AI applications with 20+ years of domain expertise.",
            "description": "Episode on London market tech.",
            "tags": "lloyds,insurance,ai"
        }

        mock_cur.fetchall.return_value = [video]

        mock_runner = MagicMock(return_value=True)
        manager = YouTubeSyncManager(db_url="postgresql://fake")
        manager.conn = mock_conn

        with patch.object(manager, "_get_connection", return_value=mock_conn), \
             patch("os.path.exists", return_value=True), \
             patch("builtins.open", unittest.mock.mock_open()):
            
            result = manager.sync_batch(limit=10, ingest_fn=mock_runner)

        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["failed"], 0)
        mock_runner.assert_called_once()
        # Ensure database was updated to mark processed
        mock_cur.execute.assert_any_call(
            "UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s",
            ("vid001",)
        )

    def test_sync_ingestion_failure_does_not_mark_processed(self):
        """Negative test: If AI ingestion fails (e.g. rate limit, crash), video remains isprocessed=False."""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        video = {
            "video_id": "vid002",
            "title": "Failing Video",
            "youtube_url": "https://youtube.com/watch?v=vid002",
            "transcript": "Transcript content that will fail during ingestion.",
            "description": "Desc",
            "tags": "fail"
        }

        mock_cur.fetchall.return_value = [video]

        # Runner returns False (ingestion failure)
        mock_runner = MagicMock(return_value=False)
        manager = YouTubeSyncManager(db_url="postgresql://fake")
        manager.conn = mock_conn

        with patch.object(manager, "_get_connection", return_value=mock_conn), \
             patch("builtins.open", unittest.mock.mock_open()):
            
            result = manager.sync_batch(limit=10, ingest_fn=mock_runner)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["failed"], 1)
        mock_runner.assert_called_once()
        
        # Verify video_id was NOT marked processed
        for call_args in mock_cur.execute.call_args_list:
            args = call_args[0]
            sql = args[0]
            if "UPDATE youtube_videos SET isprocessed = true" in sql:
                params = args[1] if len(args) > 1 else ()
                self.assertNotEqual(params, ("vid002",))

    def test_sync_non_viable_video_marked_skipped_to_prevent_infinite_loop(self):
        """Negative test: Videos without usable text are marked isprocessed=True without running AI."""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        video = {
            "video_id": "vid003_music",
            "title": "Music Track No Words",
            "youtube_url": "https://youtube.com/watch?v=vid003_music",
            "transcript": "No transcript available",
            "description": "#shorts #music #trending",
            "tags": "music"
        }

        mock_cur.fetchall.return_value = [video]

        mock_runner = MagicMock()
        manager = YouTubeSyncManager(db_url="postgresql://fake")
        manager.conn = mock_conn

        with patch.object(manager, "_get_connection", return_value=mock_conn):
            result = manager.sync_batch(limit=10, ingest_fn=mock_runner)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["skipped"], 1)
        # Ingestion function must not be called
        mock_runner.assert_not_called()
        # But DB should mark it processed so it does not block the queue
        mock_cur.execute.assert_any_call(
            "UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s",
            ("vid003_music",)
        )

    def test_db_disconnect_recovery_and_resilience(self):
        """Resilience test: Connection recovers on drop during query execution."""
        mock_conn_bad = MagicMock()
        mock_cur_bad = MagicMock()
        mock_cur_bad.execute.side_effect = psycopg2.OperationalError("Server closed connection")
        mock_conn_bad.cursor.return_value.__enter__.return_value = mock_cur_bad

        mock_conn_good = MagicMock()
        mock_cur_good = MagicMock()
        mock_cur_good.fetchall.return_value = []
        mock_conn_good.cursor.return_value.__enter__.return_value = mock_cur_good

        manager = YouTubeSyncManager(db_url="postgresql://fake")
        
        # First call fails with OperationalError, second succeeds with good connection
        with patch("psycopg2.connect", side_effect=[mock_conn_bad, mock_conn_good]):
            videos = manager.fetch_unprocessed(limit=10)
            self.assertEqual(videos, [])

    def test_stage_unprocessed(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        viable_video = {
            "video_id": "v101",
            "title": "Viable Video",
            "youtube_url": "https://youtube.com/watch?v=v101",
            "transcript": "A valid transcript for test purposes with sufficient content length.",
            "description": "Desc",
            "tags": "test"
        }
        non_viable_video = {
            "video_id": "v102_short",
            "title": "Non viable short",
            "youtube_url": "https://youtube.com/watch?v=v102",
            "transcript": "No transcript available",
            "description": "#short",
            "tags": "short"
        }

        mock_cur.fetchall.return_value = [viable_video, non_viable_video]

        manager = YouTubeSyncManager(db_url="postgresql://fake")
        manager.conn = mock_conn

        with patch.object(manager, "_get_connection", return_value=mock_conn), \
             patch("os.path.exists", return_value=False), \
             patch("builtins.open", unittest.mock.mock_open()):
            
            staged = manager.stage_unprocessed(output_dir="raw/youtube")

        self.assertEqual(len(staged), 1)
        self.assertEqual(staged[0][0], "v101")
        # Non-viable video should be marked processed immediately
        mock_cur.execute.assert_any_call(
            "UPDATE youtube_videos SET isprocessed = true WHERE video_id = %s",
            ("v102_short",)
        )

if __name__ == "__main__":
    unittest.main()
