import json,os
from scripts.synthesis_cache import SynthesisCache

def test_cache_survives_process_restart(tmp_path):
 p=tmp_path/"cache.json"; c=SynthesisCache(str(p));c.set("abc","result","topic",["source"])
 assert SynthesisCache(str(p)).exists("abc"), "Saved cache cannot be loaded after process restart"

def test_cache_invalidates_content_when_mtime_preserved(tmp_path):
 p=tmp_path/"page.md";p.write_text("old claim");c=SynthesisCache(str(tmp_path/"cache.json"));before=p.stat()
 h=c.get_hash("topic",["page"],[str(p)])
 p.write_text("new claim");os.utime(p,ns=(before.st_atime_ns,before.st_mtime_ns))
 assert h != c.get_hash("topic",["page"],[str(p)]), "Changed content with retained timestamp uses stale cache"
