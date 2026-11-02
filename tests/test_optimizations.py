import os
import pytest
from unittest.mock import MagicMock, patch
from scripts.lock import pipeline_lock, LockAcquisitionError
from scripts.synthesis_cache import SynthesisCache
from scripts.watcher import is_spend_cap_error

def test_pipeline_lock_mutual_exclusion(tmp_path):
    lock_file = tmp_path / "test_memex.lock"
    with patch("scripts.lock.LOCK_FILE", str(lock_file)):
        with pipeline_lock(blocking=False):
            # Attempt to acquire lock again while held
            with pytest.raises(LockAcquisitionError):
                with pipeline_lock(blocking=False):
                    pass

def test_spend_cap_error_detection():
    cap_msg = "429 RESOURCE_EXHAUSTED. Your project has exceeded its monthly spending cap."
    assert is_spend_cap_error(cap_msg) is True

    rpm_msg = "429 RESOURCE_EXHAUSTED. Rate limit exceeded: 15 RPM"
    assert is_spend_cap_error(rpm_msg) is False

def test_synthesis_cache_invalidation_on_content_change(tmp_path):
    cache_file = tmp_path / "cache.json"
    source_file = tmp_path / "source.md"
    source_file.write_text("Version 1 content")

    cache = SynthesisCache(cache_file=str(cache_file))
    hash1 = cache.get_hash("Test Topic", ["source"], page_files=[str(source_file)])

    # Store in cache
    cache.set(hash1, "test_synthesis", "Test Topic", ["source"])
    assert cache.exists(hash1) is True

    # Modify file mtime/content
    import time
    time.sleep(0.01)
    source_file.write_text("Version 2 updated content")
    os.utime(str(source_file), (time.time() + 10, time.time() + 10))

    hash2 = cache.get_hash("Test Topic", ["source"], page_files=[str(source_file)])
    assert hash1 != hash2
    assert cache.exists(hash2) is False
