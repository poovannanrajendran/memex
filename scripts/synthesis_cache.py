import json
import hashlib
import os
from datetime import datetime

class SynthesisCache:
    """
    Cache synthesis outputs by content hash.
    Skip re-synthesis if topic + wiki source contents haven't changed.
    """

    def __init__(self, cache_file="wiki_synthesis_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_hash(self, topic: str, page_slugs: list, page_files: list = None) -> str:
        """
        Generate hash of topic + page slugs + file content signatures.
        If file paths are provided, uses their SHA256 or mtimes so editing
        a page invalidates the cache correctly.
        """
        signatures = []
        if page_files:
            for pf in sorted(page_files):
                if os.path.exists(pf):
                    try:
                        mtime = os.path.getmtime(pf)
                        signatures.append(f"{pf}:{mtime}")
                    except Exception:
                        signatures.append(pf)
                else:
                    signatures.append(pf)
        else:
            signatures = sorted(page_slugs)

        content = f"{topic}:{'|'.join(signatures)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def exists(self, hash_val: str) -> bool:
        """Check if synthesis already cached."""
        return hash_val in self.cache

    def get(self, hash_val: str) -> dict:
        """Retrieve cached synthesis."""
        return self.cache.get(hash_val)

    def set(self, hash_val: str, synthesis_slug: str, topic: str, page_slugs: list):
        """Store new synthesis in cache."""
        self.cache[hash_val] = {
            "synthesis_slug": synthesis_slug,
            "topic": topic,
            "pages": page_slugs,
            "cached_at": datetime.utcnow().isoformat()
        }
        self._save()

    def _save(self):
        """Write cache to disk."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
            json.dump(self.cache, f, indent=2)
