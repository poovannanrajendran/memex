import pytest
from unittest.mock import MagicMock, patch
from scripts.db import Database

def test_same_size_content_change_triggers_reingest(tmp_path):
    with patch.object(Database, "__init__", return_value=None):
        db = Database()
        mock_cursor = MagicMock()
        
        from contextlib import contextmanager
        @contextmanager
        def mock_get_cursor():
            yield mock_cursor
        db.get_cursor = mock_get_cursor

        test_file = tmp_path / "article.md"
        test_file.write_text("AAAA") # length 4

        # Scenario 1: Same content hash -> skip
        import hashlib
        h1 = hashlib.sha256(b"AAAA").hexdigest()
        mock_cursor.fetchone.return_value = {
            "id": 10,
            "status": "completed",
            "file_size_bytes": 4,
            "content_hash": h1
        }
        res1 = db.register_file("run-1", str(test_file), "article", reingest_if_completed=False)
        assert res1 is None

        # Scenario 2: Same length (4), different content ("BBBB") -> triggers ingest (returns ID)
        test_file.write_text("BBBB")
        mock_cursor.fetchone.side_effect = [
            {"id": 10, "status": "completed", "file_size_bytes": 4, "content_hash": h1}, # existing
            {"id": 10} # returning id from insert/update
        ]
        res2 = db.register_file("run-2", str(test_file), "article", reingest_if_completed=False)
        assert res2 == 10
