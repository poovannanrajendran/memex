import os
import subprocess
import secrets
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from db import db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="memex Runner API")
auth_scheme = HTTPBearer()
API_SECRET = os.getenv("RUNNER_API_SECRET")

class RunRequest(BaseModel):
    trigger_source: Optional[str] = "api"

class IngestRequest(BaseModel):
    path: str
    trigger_source: Optional[str] = "api"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Secret")
    return credentials.credentials

@app.post("/run")
async def trigger_run(req: RunRequest, token: str = Depends(verify_token)):
    """Triggers the full watcher pipeline."""
    # We trigger watcher.py as a separate process to avoid blocking
    try:
        subprocess.Popen(["python3", "scripts/watcher.py"])
        return {"status": "started", "message": "Pipeline triggered via watcher.py"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def trigger_ingest(req: IngestRequest, token: str = Depends(verify_token)):
    """Ingests a specific file."""
    run_id = db.create_run(triggered_by='api', trigger_source=req.trigger_source)
    file_name = os.path.basename(req.path)
    
    # Run ingest headlessly
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("RUNNER_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
