import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Literal
from fastapi import FastAPI, Header, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import asyncio
from db import db
from dotenv import load_dotenv

load_dotenv()

WIKI_INDEX_PATH = Path(__file__).parent.parent / "wiki_index.json"
N8N_SYNC_URL    = os.getenv("N8N_MEMEX_SYNC_URL", "")
API_SECRET      = os.getenv("RUNNER_API_SECRET")
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

class RunRequest(BaseModel):
    trigger_source: Optional[str] = "api"

class IngestRequest(BaseModel):
    path: str
    trigger_source: Optional[str] = "api"
    content: Optional[str] = None
    filename: Optional[str] = None

class UrlRequest(BaseModel):
    url: str
    trigger_source: Optional[str] = "api"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Secret")
    return credentials.credentials

# --- Endpoints ---

@app.get("/ui", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the one-page Control Center UI."""
    html_path = Path(__file__).parent / "templates" / "dashboard.html"
    if not html_path.exists():
        # Fallback to a basic string if file missing
        return "<h1>Dashboard template not found</h1>"
    return html_path.read_text()

@app.post("/run")
async def trigger_run(req: RunRequest, token: str = Depends(verify_token)):
    try:
        subprocess.Popen(["python3", "scripts/watcher.py"])
        return {"status": "started", "message": "Pipeline triggered via watcher.py"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def trigger_ingest(req: IngestRequest, token: str = Depends(verify_token)):
    if req.content and req.filename:
        target_dir = Path("raw/openclaw")
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / req.filename
        target_path.write_text(req.content, encoding="utf-8")
        req = IngestRequest(path=str(target_path), trigger_source=req.trigger_source or "openclaw")

    run_id = db.create_run(triggered_by='api', trigger_source=req.trigger_source)
    try:
        subprocess.Popen(["python3", "scripts/ingest.py", req.path, str(run_id)])
        return {"run_id": str(run_id), "file": os.path.basename(req.path), "status": "started"}
    except Exception as e:
        db.complete_run(run_id, 'failed', 1, 0, 0, 1, error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/url")
async def trigger_url_fetch(req: UrlRequest, token: str = Depends(verify_token)):
    try:
        subprocess.Popen(["python3", "scripts/add_url.py", req.url])
        return {"status": "started", "message": f"URL fetch initiated for {req.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    category: str = Form(...), 
    token: str = Depends(verify_token)
):
    """Saves an uploaded file to the correct raw/ directory."""
    valid_categories = ["articles", "pdfs", "transcripts", "youtube", "posts"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    target_path = Path(f"raw/{category}") / file.filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"status": "success", "path": str(target_path)}

@app.get("/status")
async def get_status():
    with db.get_cursor() as cur:
        cur.execute("""
            SELECT r.run_id, r.triggered_by, r.trigger_source, r.started_at, r.status, r.files_processed, s.estimated_cost_usd
            FROM pipeline_runs r
            LEFT JOIN ai_call_summary s ON r.run_id = s.run_id
            ORDER BY r.started_at DESC LIMIT 10
        """)
        return {"last_runs": cur.fetchall()}

@app.get("/search")
async def search_wiki(q: str, type: Optional[str] = None, limit: int = 10, token: str = Depends(verify_token)):
    index = _load_wiki()
    q_lower = q.lower()
    results = []
    sections = [type] if type else ["synthesis", "sources", "entities", "concepts"]
    for section in sections:
        for slug, entry in index.get(section, {}).items():
            haystack = f"{entry.get('title','')} {entry.get('summary','')}".lower()
            if q_lower in haystack:
                results.append({"type": section, "slug": slug, "title": entry.get("title", slug)})
            if len(results) >= limit: break
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
