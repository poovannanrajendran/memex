# Memex ↔ OpenClaw Integration Spec

**Version:** 1.0  
**Date:** 2026-05-01  
**Status:** Implementation ready  
**Managed by:** Gemini CLI (Memex side) + OpenClaw config (OpenClaw side)

---

## 1. Purpose

This document specifies the full bidirectional integration between **Memex** (Poovi's Second Brain, running on `automation-runner-01` at `192.168.1.30`) and **OpenClaw** (AI agent gateway, running on `ai-node-01` at `192.168.1.24`).

Once implemented, every OpenClaw agent can recall Memex knowledge automatically — and agents can write new research back into Memex as raw source files.

---

## 2. Bidirectional Data Flows

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMEX (automation-runner-01)                │
│                                                                  │
│   raw/ → watcher.py → ingest.py → wiki/ → git push → Vercel    │
│                            │                                     │
│                    Post-ingest hook (NEW)                        │
│                            │                                     │
└────────────────────────────┼────────────────────────────────────┘
                             │
           ┌─────────────────┼──────────────────┐
           │                 │                  │
           ▼                 ▼                  ▼
    Path A: Bulk       Path B: MCP         Path C: n8n
    Ingest             Live Search         Incremental
    (one-time)         (on demand)         (per-run)
           │                 │                  │
           └────────┬────────┘                  │
                    ▼                            ▼
              Qdrant                     Qdrant (updated
         memex-knowledge                 incrementally)
              collection
                    │
                    ▼
         OpenClaw Agents (all)
         ← AutoRecall via Mem0

┌─────────────────────────────────────────────────────────────────┐
│                   OPENCLAW → MEMEX (write-back)                 │
│                                                                  │
│   Agent produces research/content                               │
│        ↓                                                        │
│   POST /ingest to runner_api (trigger_source: 'openclaw')       │
│        ↓                                                        │
│   watcher.py picks up file in raw/openclaw/                     │
│        ↓                                                        │
│   ingest.py processes → wiki pages created → git push           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Flows: Memex → OpenClaw

### 3.1 Path A — Bulk Ingest (One-time Seed)

**Trigger:** Manual, run once from Mac or automation-runner-01  
**Script:** `scripts/openclaw_ingest.py`  
**Target:** Qdrant collection `memex-knowledge` on `192.168.1.20:6333`  
**Volume:** ~7,483 pages (603 sources, 1,821 entities, 5,046 concepts, 8 synthesis)  
**Frequency:** Once, then re-run after major Memex rebuilds

**What it does:**
- Reads `wiki_index.json`
- Extracts title + summary + keywords + frontmatter for each entry
- Pushes all entries as Qdrant points in `memex-knowledge` collection
- Each point has payload: `{type, slug, title, summary, file_path, source: "memex"}`

**Run:**
```bash
cd /home/labadmin/memex
QDRANT_HOST=http://192.168.1.20:6333 python3 scripts/openclaw_ingest.py
```

---

### 3.2 Path B — Live MCP Search (On Demand)

**Trigger:** OpenClaw agent calls `memex_search`, `memex_get`, or `memex_synthesis_list` tool  
**Transport:** stdio MCP via SSH (OpenClaw → ai-node-01 → SSH → automation-runner-01 → memex_mcp.py → runner_api)  
**Latency:** ~200–400ms per tool call (SSH + HTTP roundtrip)

**Endpoints exposed by runner_api (NEW):**

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/search` | GET | Full-text search wiki_index.json. Params: `q`, `type`, `limit` |
| `/wiki/{type}/{slug}` | GET | Fetch specific entry + full markdown content |
| `/wiki/synthesis/list` | GET | List all synthesis docs (highest-value content) |

**MCP tools available to OpenClaw agents:**

| Tool | When to use |
|------|-------------|
| `memex_synthesis_list` | First — get overview of deep-dive analyses |
| `memex_search` | Search concepts, entities, sources by keyword |
| `memex_get` | Fetch full content of a specific known entry |

**Usage patterns by agent:**

| Agent | Typical query |
|-------|--------------|
| `market-intel` | `memex_search("lloyd's market AI underwriting")` |
| `career-brand` | `memex_search("poovi career positioning", type="entities")` |
| `main` | `memex_synthesis_list()` then `memex_get("synthesis", slug)` |
| `coding` | `memex_search("nextjs supabase pattern", type="concepts")` |

---

### 3.3 Path C — Incremental Sync (Per Watcher Run)

**Trigger:** watcher.py completes a run with `processed > 0` (new files ingested)  
**Transport:** HTTP POST to n8n webhook on automation-runner-01  
**n8n endpoint:** `http://192.168.1.30:5678/webhook/memex-ingest`  
**Latency:** ~3–5 minutes after watcher run completes  

**Payload sent per new page:**
```json
{
  "event": "memex_ingested",
  "run_id": "<uuid>",
  "type": "sources | entities | concepts | synthesis",
  "slug": "the_page_slug",
  "title": "Page Title",
  "summary": "First 300 chars of summary",
  "file_path": "wiki/sources/the_page_slug.md",
  "trigger_source": "openclaw"
}
```

**n8n workflow:** Receives payload → upserts Qdrant point in `memex-knowledge` → optional Telegram notification

---

### 3.4 Synthesis Auto-Push (High Priority)

Synthesis docs are the highest-value content in Memex. When a new synthesis is created:
- watcher.py sends a **synthesis-specific** webhook payload
- n8n pushes the full synthesis text (not just summary) to Qdrant
- Also writes a `memory-wiki` entry on ai-node-01 for structured recall

This ensures synthesis docs appear in OpenClaw recall with higher weight than standard pages.

---

## 4. Flows: OpenClaw → Memex (Write-Back)

Agents can contribute new knowledge back to Memex. This closes the loop: OpenClaw agents research → write to Memex → Memex ingests → re-indexed → recalled by future agents.

### 4.1 Agent Creates New Source File

**How:** Agent writes a markdown file to `raw/openclaw/` via the runner_api `/ingest` endpoint.  
**Trigger:** `POST /ingest` with `path` pointing to the newly written file and `trigger_source: "openclaw"`  
**Result:** watcher.py picks up the file on next run (or immediate if `/run` also called) → full ingest pipeline → wiki pages created → git push → Vercel update

**Agent-facing usage (from Telegram):**
```
Spawn market-intel to research Lloyd's AI adoption Q1 2026 and write a Memex source file.
```

market-intel agent workflow:
1. Research topic using browser/search tools
2. Format as Memex source markdown (source template — see GEMINI.md)
3. POST to runner_api `/ingest` with the file content and path `raw/openclaw/{slug}.md`
4. Confirm with run_id

### 4.2 Source File Format for Agent Write-Back

Files written by OpenClaw agents MUST follow this template:

```markdown
---
title: "[Research title]"
source_type: transcript
url: ""
ingested: YYYY-MM-DD
confidence: medium
tags: [openclaw, agent-research, market-intel]
agent_id: market-intel
trigger_source: openclaw
---

## Summary
[Agent-written summary]

## Key claims
- [Claim]

## Entities mentioned
- [[Entity]]

## Concepts covered
- [[Concept]]

## Contradictions or open questions
[Any conflicts with existing Memex knowledge]

## Source
Agent research — {agent_id} — {date}
```

### 4.3 Ingest Endpoint Extended (NEW)

The existing `/ingest` endpoint accepts a `path` to an existing file. Extend it to also accept raw markdown content:

```python
class IngestRequest(BaseModel):
    path: str                            # existing field
    trigger_source: Optional[str] = "api"
    content: Optional[str] = None        # NEW: raw markdown content
    filename: Optional[str] = None       # NEW: filename to write if content provided
```

When `content` is provided, runner_api writes it to `raw/openclaw/{filename}` before triggering ingest.

---

## 5. Files Changed / Created

### 5.1 Modified: `scripts/runner_api.py`

**Changes:**
- Add `/search` GET endpoint (wiki_index.json full-text search)
- Add `/wiki/{type}/{slug}` GET endpoint (full entry fetch + markdown)
- Add `/wiki/synthesis/list` GET endpoint
- Extend `IngestRequest` with `content` and `filename` fields
- Add async `notify_openclaw_sync()` function called after successful ingest

### 5.2 Modified: `scripts/watcher.py`

**Changes:**
- After step 7 (git push), call `notify_openclaw()` with list of processed files
- Pass `run_id` and list of `{type, slug, title, summary, file_path}` for each new wiki page

### 5.3 New: `scripts/openclaw_ingest.py`

One-time bulk ingest of `wiki_index.json` → Qdrant `memex-knowledge`.

### 5.4 New: `scripts/memex_mcp.py`

stdio MCP server wrapping runner_api. Exposes three tools: `memex_search`, `memex_get`, `memex_synthesis_list`.

### 5.5 Modified: `GEMINI.md`

**Additions:**
- New section: `## OpenClaw Integration` — describes the integration, agent write-back format, and new slash command
- New slash command: `/second-brain-openclaw-push [topic]` — agent researches and writes a new Memex source file

### 5.6 Modified: `.env.example`

**Additions:**
```
N8N_MEMEX_SYNC_URL=http://192.168.1.30:5678/webhook/memex-ingest
OPENCLAW_NOTIFY_ENABLED=true
QDRANT_HOST=http://192.168.1.20:6333
```

---

## 6. Security Notes

| Item | Risk | Mitigation |
|------|------|-----------|
| RUNNER_API_SECRET in OpenClaw config | Token exposed if config file compromised | File owned by `openclaw` user, mode 600 |
| SSH key for `openclaw` → automation-runner-01 | Key allows MCP process execution | Restrict to specific command in `authorized_keys` using `command=` forced command |
| Agent write-back to `raw/openclaw/` | Agent could write malicious content | runner_api validates markdown structure; Gemini CLI reviews on ingest |
| Qdrant no auth | LAN exposure | Bind to LAN only; add API key if WAN access ever needed |

**Recommended `authorized_keys` entry for `openclaw` user** (forced command restricts to MCP script only):
```
command="python3 /home/labadmin/memex/scripts/memex_mcp.py",no-port-forwarding,no-X11-forwarding ssh-ed25519 AAAA... openclaw@ai-node-01
```

---

## 7. Verification Checklist

### Path A (Bulk Ingest)
- [ ] `openclaw_ingest.py` runs without errors
- [ ] Qdrant dashboard shows `memex-knowledge` collection with ~7,483 points
- [ ] OpenClaw agent recalls Memex content in new session

### Path B (MCP Search)
- [ ] `memex_mcp.py` responds to `tools/list` with three tools
- [ ] `/search?q=lloyds&limit=5` returns JSON results
- [ ] `openclaw mcp list` shows `memex`
- [ ] Agent can search Memex from Telegram

### Path C (Incremental Sync)
- [ ] Drop a file in `raw/articles/`, trigger watcher
- [ ] n8n execution log shows webhook received
- [ ] Qdrant point count increases

### Write-back
- [ ] POST `/ingest` with `content` + `filename` creates file in `raw/openclaw/`
- [ ] watcher picks up file and processes with `trigger_source: openclaw`
- [ ] New wiki page appears on `memex.poovi.me`

---

## 8. Ongoing Maintenance

| Task | Frequency | Who |
|------|-----------|-----|
| Re-run `openclaw_ingest.py` | After major Memex rebuilds or 1000+ new pages | Manual |
| Review `raw/openclaw/` files | Weekly | Gemini CLI lint pass |
| Monitor Qdrant collection size | Monthly | Grafana (after Prometheus scrape added) |
| Rotate RUNNER_API_SECRET | Quarterly | Manual + update OpenClaw config |
| Review agent write-back quality | Monthly | Gemini CLI synthesis pass |
