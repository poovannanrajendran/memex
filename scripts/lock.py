import os
import fcntl
from contextlib import contextmanager

LOCK_FILE = "/tmp/memex_pipeline.lock"

class LockAcquisitionError(Exception):
    """Raised when unable to acquire pipeline lock."""
    pass

@contextmanager
def pipeline_lock(blocking=False):
    """
    Acquires an exclusive file lock to prevent overlapping runs 
    between watcher cron jobs, runner_api endpoints, and CLI triggers.
    """
    lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR, 0o666)
    flags = fcntl.LOCK_EX if blocking else (fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        fcntl.flock(lock_fd, flags)
        yield
    except (BlockingIOError, OSError) as e:
        raise LockAcquisitionError("Another memex pipeline or watcher is already running.") from e
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        except Exception:
            pass
        os.close(lock_fd)
