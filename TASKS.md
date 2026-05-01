# TASKS.md — Second Brain Build Plan

> KISS: no ceremonies, no sprint planning, no story points.
> Work through phases in order. Tick tasks as done. Commit after each.

---

## Phase 1 — Fork and run ✅
**Goal:** A working vault with Gemini CLI driving real ingestion within one session.

- [x] Fork `NicholasSpisak/second-brain` to your GitHub account
- [x] Clone locally
- [x] Run setup wizard and initial context setup
- [x] Initialise Git tracking on the vault
- [x] Ingest test sources and verify graph connectivity
- [x] Confirm `wiki/index.md` and `wiki/log.md` are populated

**Done when:** Three sources ingested, graph view shows linked pages.

---

## Phase 2 — YouTube database integration ✅
**Goal:** Pipe the existing YouTube liked-video database into the vault.

- [x] Direct PostgreSQL integration (`192.168.1.20`)
- [x] Write `scripts/youtube_watcher.py` for delta processing
- [x] Batch-ingest the YouTube records: 770+ videos processed
- [x] Fix broken wikilinks via automated stubbing (`scripts/autofix_links.py`)
- [x] Verify the Obsidian graph is fully interconnected (7,000+ pages)

**Done when:** All YouTube records are ingested, speaker and concept pages exist.

---

## Phase 3 — Gemini API pipeline ✅
**Goal:** High-performance headless ingestion.

- [x] Create `scripts/ingest.py` with structured JSON output
- [x] Implement Gemini 2.5 Flash Lite for cost efficiency
- [x] Add description fallback for missing transcripts
- [x] Add robust YAML title escaping for Quartz stability
- [x] Add automated Git sync to ingestion pipeline

**Done when:** Ingestion runs headlessly with automated commits and pushes.

---

## Phase 4 — Autonomous Infrastructure ✅
**Goal:** The wiki maintains itself on a dedicated server.

- [x] Migrate pipeline to `automation-runner-01` (`192.168.1.30`)
- [x] Configure dedicated `venv` with all dependencies
- [x] Schedule hourly watcher cron job (:18 past each hour)
- [x] Enable automated GitHub sync via HTTPS
- [x] Zero-maintenance index reconstruction (`scripts/rebuild_index_md.py`)

**Done when:** Server processes videos, commits, and pushes autonomously.

---

## Phase 5 — Portfolio polish 🚧
**Goal:** The project is interview-ready and publicly demonstrable.

- [ ] Write a clean `README.md`
- [ ] Export a static snapshot of the wiki
- [ ] Record a 3-minute walkthrough video
- [ ] Add the project to `poovi.me` portfolio page
- [ ] Push the repo public

**Done when:** README is complete, repo is public, walkthrough video is recorded.

---

## Phase 6 — OpenClaw Integration 🚧
**Goal:** Memex knowledge is accessible to all OpenClaw agents with bidirectional sync.

**Reference:** `docs/openclaw-integration.md` for full spec.

### 6.1 Code changes (apply via Gemini CLI)
- [x] Apply Change 1 to `scripts/runner_api.py` (search/wiki endpoints + write-back)
- [x] Apply Change 2 to `scripts/watcher.py` (OpenClaw notification after git push)
- [x] Apply Change 3 to `.env.example` (new env vars)
- [x] Create `raw/openclaw/` directory (with `.gitkeep`)
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
