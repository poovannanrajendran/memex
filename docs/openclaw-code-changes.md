# OpenClaw Integration — Exact Code Changes

> **For Gemini CLI:** Apply these changes to the Memex codebase exactly as specified.
> Each section identifies the file, the insertion point, and the code to add.
> After all changes, run tests, commit, and push.

---

## Change 1: `scripts/runner_api.py` — Add search/wiki endpoints + write-back + webhook

### 1a. Add imports (after existing imports block)

Find this line:
```python
from dotenv import load_dotenv
```

Add immediately after:
```python
from pathlib import Path
import httpx
import asyncio
```

---

### 1b. Add wiki index cache (after `load_dotenv()` and before `app = FastAPI(...)`)

```python
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
```

---

### 1c. Extend IngestRequest (replace existing class)

Replace:
```python
class IngestRequest(BaseModel):
    path: str
    trigger_source: Optional[str] = "api"
```

With:
```python
class IngestRequest(BaseModel):
    path: str
    trigger_source: Optional[str] = "api"
    content: Optional[str] = None       # raw markdown — written to raw/openclaw/{filename}
    filename: Optional[str] = None      # required when content is provided
```

---

### 1d. Update /ingest endpoint to handle content write-back

Find the `/ingest` endpoint. After the `run_id = db.create_run(...)` line, add:

```python
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
```

---

### 1e. Add async OpenClaw notification function (before the existing routes)

```python
async def _notify_openclaw_sync(pages: list[dict], run_id: str):
    """Fire-and-forget POST to n8n webhook with newly ingested pages."""
    if not N8N_SYNC_URL or not pages:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            for page in pages:
                await client.post(N8N_SYNC_URL, json={
                    "event": "memex_ingested",
                    "run_id": run_id,
                    **page,
                    "trigger_source": "openclaw"
                })
    except Exception as e:
        print(f"[openclaw notify] Failed: {e}")
```

---

### 1f. Add three new GET endpoints (add after the existing /status route)

```python
from typing import Literal

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
```

---

## Change 2: `scripts/watcher.py` — Add OpenClaw notification after git push

### 2a. Add import at top of file

Find:
```python
from db import db
```

Add after:
```python
import json as _json
```

---

### 2b. Add notification function (add after the `run_ingest` function, before `watch()`)

```python
def notify_openclaw(run_id: str, processed_files: list):
    """Post newly ingested wiki pages to n8n for Qdrant sync."""
    n8n_url = os.getenv("N8N_MEMEX_SYNC_URL", "")
    if not n8n_url or not processed_files:
        return

    # Load wiki_index to get metadata for processed files
    wiki_index_path = "wiki_index.json"
    if not os.path.exists(wiki_index_path):
        return

    with open(wiki_index_path) as f:
        index = _json.load(f)

    import requests as _req
    for fpath in processed_files:
        # Derive slug from file path: wiki/sources/foo.md → "foo"
        slug = os.path.splitext(os.path.basename(fpath))[0]
        entry_type = None
        entry = None
        for t in ["sources", "entities", "concepts", "synthesis"]:
            if slug in index.get(t, {}):
                entry_type = t
                entry = index[t][slug]
                break
        if not entry_type:
            continue
        try:
            _req.post(n8n_url, json={
                "event": "memex_ingested",
                "run_id": str(run_id),
                "type": entry_type,
                "slug": slug,
                "title": entry.get("title", slug),
                "summary": (entry.get("summary") or "")[:400],
                "file_path": entry.get("file_path", fpath),
                "trigger_source": "openclaw"
            }, timeout=5)
        except Exception as e:
            print(f"[openclaw notify] {slug}: {e}")
```

---

### 2c. Track processed file paths in the watch() function

In `watch()`, find the section where files are processed:
```python
    for file_id, fpath in work_queue:
        if run_ingest(run_id, file_id, fpath):
            processed += 1
        else:
            failed += 1
```

Replace with:
```python
    processed_paths = []
    for file_id, fpath in work_queue:
        if run_ingest(run_id, file_id, fpath):
            processed += 1
            processed_paths.append(fpath)
        else:
            failed += 1
```

---

### 2d. Call notify_openclaw after git push

Find:
```python
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Successfully synced. Probing Vercel deployment...")
            subprocess.run(["python3", "scripts/probe_vercel.py"], check=True)
        except Exception as e:
            print(f"Post-ingest sync/probe failed: {e}")
```

Replace with:
```python
        try:
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("Successfully synced. Probing Vercel deployment...")
            subprocess.run(["python3", "scripts/probe_vercel.py"], check=True)
            # Notify OpenClaw of new pages
            notify_openclaw(run_id, processed_paths)
        except Exception as e:
            print(f"Post-ingest sync/probe failed: {e}")
```

---

## Change 3: `.env.example` — Add new variables

Add to the end of `.env.example`:

```bash
# --- OpenClaw Integration ---
# n8n webhook URL for incremental Qdrant sync
N8N_MEMEX_SYNC_URL=http://192.168.1.30:5678/webhook/memex-ingest

# Qdrant host for bulk ingest script
QDRANT_HOST=http://192.168.1.20:6333

# Set to false to disable OpenClaw notifications
OPENCLAW_NOTIFY_ENABLED=true
```

---

## Change 4: `TASKS.md` — Add Phase 6

Append to `TASKS.md`:

```markdown
---

## Phase 6 — OpenClaw Integration 🚧
**Goal:** Memex knowledge is accessible to all OpenClaw agents with bidirectional sync.

**Reference:** `docs/openclaw-integration.md` for full spec.

### 6.1 Code changes (apply via Gemini CLI)
- [ ] Apply Change 1 to `scripts/runner_api.py` (search/wiki endpoints + write-back)
- [ ] Apply Change 2 to `scripts/watcher.py` (OpenClaw notification after git push)
- [ ] Apply Change 3 to `.env.example` (new env vars)
- [ ] Create `raw/openclaw/` directory (with `.gitkeep`)
- [ ] Restart `memex-runner.service` after changes
- [ ] Set `N8N_MEMEX_SYNC_URL` in live `.env` on automation-runner-01

### 6.2 Verify runner_api endpoints (from automation-runner-01)
- [ ] `GET /search?q=lloyds&limit=5` returns JSON results
- [ ] `GET /wiki/synthesis/list` returns 8 items
- [ ] `GET /wiki/synthesis/ai_agent_frameworks_and_the_challenge_of_standardised_memory` returns full content
- [ ] `POST /ingest` with `content` + `filename` creates file in `raw/openclaw/`

### 6.3 Bulk ingest to Qdrant (from automation-runner-01 or Mac)
- [ ] Run `scripts/openclaw_ingest.py --dry-run` — confirm counts
- [ ] Run `scripts/openclaw_ingest.py` — seed Qdrant
- [ ] Verify `memex-knowledge` collection on `http://192.168.1.20:6333/dashboard`

### 6.4 MCP server (on automation-runner-01)
- [ ] `chmod +x scripts/memex_mcp.py`
- [ ] Test locally: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 scripts/memex_mcp.py`
- [ ] Confirm SSH key for `openclaw` user added to `~/.ssh/authorized_keys`

### 6.5 OpenClaw config (on ai-node-01 — handled separately)
- [ ] MCP server registered in `~/.openclaw/config.json5`
- [ ] `openclaw mcp list` shows `memex`
- [ ] Agent searches Memex from Telegram ✓

### 6.6 n8n sync workflow (on automation-runner-01 n8n)
- [ ] Build "Memex → Qdrant Sync" webhook workflow
- [ ] Activate workflow
- [ ] Test end-to-end: drop file in `raw/`, trigger watcher, confirm n8n fires, confirm Qdrant updates

**Done when:** Agent can search Memex from Telegram, new ingests appear in Qdrant within 5 minutes.
```

---

## Change 5: `GEMINI.md` — Add OpenClaw Integration section

> **Important:** GEMINI.md must not be modified during normal operation.  
> Apply this change deliberately via a separate git commit with message: `docs: add OpenClaw integration to GEMINI.md`

Append the following section to the end of `GEMINI.md` (before "## What to never do"):

---

```markdown
## OpenClaw Integration

Memex is connected to **OpenClaw** (Poovi's self-hosted AI agent gateway on `ai-node-01`).
This section defines how Gemini CLI interacts with the integration.

### What this means for wiki maintenance

1. **`raw/openclaw/`** is a valid source directory. Files dropped here by OpenClaw agents  
   follow the same ingest rules as `raw/articles/`. Source type: `transcript`.  
   Always tag them with `openclaw` and `agent-research` in frontmatter.

2. **After every watcher run**, a notification is sent to n8n which syncs new wiki pages  
   to Qdrant on `docker-host-01`. This is automatic — no action required.

3. **`wiki_index.json`** is read by OpenClaw agents for live search. It is rebuilt on  
   every `npm run build`. After bulk wiki changes (100+ pages), rebuild the index:  
   ```bash
   node quartz/bootstrap-cli.mjs build
   ```

4. **Synthesis docs** are highest-priority for OpenClaw agents. When creating a new  
   synthesis, also update `wiki_index.json` by rebuilding. The synthesis content is  
   injected into agent context with higher weight than source/entity/concept pages.

### New slash command: /second-brain-openclaw-push [topic]

**Purpose:** Research a topic and write a new source file to `raw/openclaw/` for Memex ingestion.  
This is used when an OpenClaw agent (typically `market-intel`) asks Memex to absorb new research.

**Steps:**
1. Research the topic using available knowledge and sources.
2. Format the research as a Memex source page (use the `wiki/sources/` template).
3. Set frontmatter: `source_type: transcript`, `tags: [openclaw, agent-research]`, `agent_id: <caller>`.
4. Write to `raw/openclaw/[slug].md`.
5. POST to runner_api `/ingest` with `path: raw/openclaw/[slug].md`, `trigger_source: openclaw`.
6. Confirm with `run_id` from response.
7. Log in `wiki/log.md`:  
   `**Operation:** openclaw-push | **Input:** [topic] | **Output:** [slug].md created`

**Never write sensitive data** (API keys, passwords, personal contact details) to `raw/openclaw/`.

### Write-back file format

All files written to `raw/openclaw/` must use this template:

```markdown
---
title: "[Title of the research]"
source_type: transcript
url: ""
ingested: YYYY-MM-DD
confidence: medium
tags: [openclaw, agent-research, <agent_id>]
agent_id: <openclaw-agent-id>
trigger_source: openclaw
---

## Summary
[2-4 sentence summary]

## Key claims
- [Claim]

## Entities mentioned
- [[Entity]]

## Concepts covered
- [[Concept]]

## Contradictions or open questions
[Conflicts with existing Memex knowledge, if any]

## Source
Agent research — {agent_id} — {YYYY-MM-DD}
```

### runner_api endpoints (available on localhost:8000)

| Endpoint | Method | Auth | Description |
|---------|--------|------|-------------|
| `/search` | GET | Bearer | Search wiki_index.json — params: `q`, `type`, `limit` |
| `/wiki/{type}/{slug}` | GET | Bearer | Fetch full wiki entry + markdown |
| `/wiki/synthesis/list` | GET | Bearer | List all synthesis docs |
| `/ingest` | POST | Bearer | Trigger ingest — accepts `content` + `filename` for write-back |
| `/run` | POST | Bearer | Trigger full watcher pipeline |
| `/status` | GET | Bearer | Last 5 pipeline runs |
```

---

## Commit Message

After applying all changes:

```
feat: add OpenClaw integration — search API, MCP server, bulk ingest, watcher webhook

- runner_api.py: add /search, /wiki/{type}/{slug}, /wiki/synthesis/list endpoints
- runner_api.py: extend /ingest to accept raw content for agent write-back
- watcher.py: notify n8n after successful ingest for Qdrant incremental sync
- scripts/openclaw_ingest.py: new — bulk ingest wiki_index.json to Qdrant
- scripts/memex_mcp.py: new — stdio MCP server for OpenClaw tool access
- docs/openclaw-integration.md: new — full integration spec
- docs/openclaw-code-changes.md: new — change instructions for Gemini CLI
- TASKS.md: add Phase 6 OpenClaw integration tasks
- GEMINI.md: add OpenClaw integration section + /second-brain-openclaw-push command
- .env.example: add N8N_MEMEX_SYNC_URL, QDRANT_HOST, OPENCLAW_NOTIFY_ENABLED
```
