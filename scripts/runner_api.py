import os
import json
import subprocess
import secrets
from pathlib import Path
from typing import Optional, Literal
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import asyncio
from db import db
from dotenv import load_dotenv

load_dotenv()

WIKI_INDEX_PATH = Path(__file__).parent.parent / "wiki_index.json"
N8N_SYNC_URL    = os.getenv("N8N_MEMEX_SYNC_URL", "")
_wiki_cache: dict = {}

def _load_wiki() -> dict:
    global _wiki_cache
    if not _wiki_cache:
        if not WIKI_INDEX_PATH.exists():
            return {}
        with open(WIKI_INDEX_PATH) as f:
            _wiki_cache = json.load(f)
    return _wiki_cache

app = FastAPI(title="memex Runner API")
auth_scheme = HTTPBearer()
API_SECRET = os.getenv("RUNNER_API_SECRET")

class RunRequest(BaseModel):
    trigger_source: Optional[str] = "api"

class IngestRequest(BaseModel):
    path: str
    trigger_source: Optional[str] = "api"
    content: Optional[str] = None       # raw markdown — written to raw/openclaw/{filename}
    filename: Optional[str] = None      # required when content is provided

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Secret")
    return credentials.credentials

async def _notify_openclaw_sync(pages: list[dict], run_id: str):
    """Fire-and-forget POST to n8n webhook with newly ingested pages."""
    if not N8N_SYNC_URL or not pages:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            for page in pages:
                await client.post(N8N_SYNC_URL, json={
                    "event": "memex_ingested",
                    "run_id": str(run_id),
                    **page,
                    "trigger_source": "openclaw"
                })
    except Exception as e:
        print(f"[openclaw notify] Failed: {e}")

@app.post("/run")
async def trigger_run(req: RunRequest, token: str = Depends(verify_token)):
    """Triggers the full watcher pipeline."""
    try:
        subprocess.Popen(["python3", "scripts/watcher.py"])
        return {"status": "started", "message": "Pipeline triggered via watcher.py"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def trigger_ingest(req: IngestRequest, token: str = Depends(verify_token)):
    """Ingests a specific file."""
    
    # Write-back: if content provided, save to raw/openclaw/ before ingest
    if req.content and req.filename:
        target_dir = Path("raw/openclaw")
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / req.filename
        target_path.write_text(req.content, encoding="utf-8")
        req = IngestRequest(
            path=str(target_path),
            trigger_source=req.trigger_source or "openclaw",
            content=None,
            filename=None
        )

    run_id = db.create_run(triggered_by='api', trigger_source=req.trigger_source)
    file_name = os.path.basename(req.path)
    
    try:
        subprocess.Popen(["python3", "scripts/ingest.py", req.path, str(run_id)])
        return {
            "run_id": str(run_id),
            "file": file_name,
            "status": "started"
        }
    except Exception as e:
        db.complete_run(run_id, 'failed', 1, 0, 0, 1, error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Returns the last 5 pipeline runs."""
    with db.get_cursor() as cur:
        cur.execute("""
            SELECT 
                r.run_id,
                r.triggered_by,
                r.trigger_source,
                r.started_at,
                r.status,
                r.files_processed,
                s.estimated_cost_usd
            FROM pipeline_runs r
            LEFT JOIN ai_call_summary s ON r.run_id = s.run_id
            ORDER BY r.started_at DESC
            LIMIT 5
        """)
        runs = cur.fetchall()
        return {"last_runs": runs}

@app.get("/search")
async def search_wiki(
    q: str,
    type: Optional[Literal["sources", "entities", "concepts", "synthesis"]] = None,
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """Full-text keyword search across wiki_index.json."""
    index = _load_wiki()
    if not index:
        raise HTTPException(status_code=503, detail="wiki_index.json not loaded")

    q_lower = q.lower()
    results = []
    sections = [type] if type else ["synthesis", "sources", "entities", "concepts"]

    for section in sections:
        for slug, entry in index.get(section, {}).items():
            haystack = " ".join([
                entry.get("title", ""),
                entry.get("summary", "") or "",
                " ".join(entry.get("keywords", [])),
                entry.get("frontmatter", {}).get("domain", "")
            ]).lower()
            if q_lower in haystack:
                results.append({
                    "type": section,
                    "slug": slug,
                    "title": entry.get("title", slug),
                    "summary": (entry.get("summary") or "")[:400],
                    "file_path": entry.get("file_path", ""),
                    "domain": entry.get("frontmatter", {}).get("domain", ""),
                    "confidence": entry.get("frontmatter", {}).get("confidence", ""),
                    "last_updated": entry.get("frontmatter", {}).get("last_updated", "")
                })
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    return {
        "query": q,
        "type_filter": type,
        "total": len(results),
        "results": results
    }

@app.get("/wiki/{entry_type}/{slug}")
async def get_wiki_entry(
    entry_type: Literal["sources", "entities", "concepts", "synthesis"],
    slug: str,
    token: str = Depends(verify_token)
):
    """Fetch a specific wiki entry by type + slug. Returns index data + full markdown."""
    index = _load_wiki()
    entry = index.get(entry_type, {}).get(slug)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Not found: {entry_type}/{slug}")

    full_content = None
    file_path = entry.get("file_path", "")
    if file_path:
        md_path = Path(__file__).parent.parent / file_path
        if md_path.exists():
            full_content = md_path.read_text(encoding="utf-8")

    return {
        "type": entry_type,
        "slug": slug,
        "title": entry.get("title", slug),
        "summary": entry.get("summary", ""),
        "keywords": entry.get("keywords", []),
        "frontmatter": entry.get("frontmatter", {}),
        "file_path": file_path,
        "full_content": full_content
    }

@app.get("/wiki/synthesis/list")
async def list_synthesis(token: str = Depends(verify_token)):
    """List all synthesis documents — the highest-value content for OpenClaw agents."""
    index = _load_wiki()
    synthesis = index.get("synthesis", {})
    return [
        {
            "slug": slug,
            "title": e.get("title", slug),
            "summary": (e.get("summary") or "")[:300],
            "sources_count": len(e.get("frontmatter", {}).get("sources", [])),
            "created": e.get("frontmatter", {}).get("created", "")
        }
        for slug, e in synthesis.items()
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("RUNNER_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
