# memex — Project Handoff Document

## 1. Project Overview
**memex** is a production-grade personal knowledge base built on the **LLM Wiki Pattern**. It uses a three-layer architecture to ingest raw source materials (articles, PDFs, transcripts) and transform them into a structured, interlinked wiki maintained by a Gemini-powered AI agent.

- **URL**: [https://memex-poovi.vercel.app/](https://memex-poovi.vercel.app/)
- **Repository**: [github.com/poovannanrajendran/memex](https://github.com/poovannanrajendran/memex)
- **Primary Model**: Google Gemini 2.5 Pro (Synthesis) & 2.5 Flash-Lite (Ingestion)

---

## 2. Key Components & Infrastructure

### **A. The Automation Engine (Proxmox)**
Located on `automation-runner-01` (`/home/labadmin/memex`).
- **`watcher.py`**: The "Brain" that polls for new files in `raw/`, orchestrates the pipeline, and pushes to GitHub.
- **`runner_api.py`**: A FastAPI service for remote triggers (OpenClaw/Telegram).
- **`scripts/db.py`**: Shared PostgreSQL module for logging, deduplication, and 2026-ready cost tracking ($/1M tokens).

### **B. The Database (PostgreSQL)**
Located at `192.168.1.30:5432/memex`.
- Tracks every pipeline run, step, and individual AI API call.
- Provides a full audit trail of token consumption and USD costs.

### **C. The Public Wiki (Vercel)**
Deployed via **Quartz** to `memex.poovi.me`.
- **Auto-Sync**: Triggered automatically by the runner's `git push`.
- **`probe_vercel.py`**: A verification script run by the watcher to ensure the site is live after an update.

---

## 3. Operational Guide

### **Standard Ingestion Loop**
1.  **Capture**: Drop a new file into a subfolder of `raw/` on the runner.
2.  **Wait**: The cron job (`scripts/setup_cron.sh`) triggers `watcher.py` every 15 minutes.
3.  **Monitor**: View progress in the `pipeline_runs` table or check `/var/log/memex-watcher.log`.
4.  **View**: Changes appear on `memex.poovi.me` within ~3 minutes.

### **Manual Controls**
- **Force Run**: `python3 scripts/watcher.py`
- **Manual Ingest**: `python3 scripts/ingest.py path/to/file.md`
- **Topic Synthesis**: `python3 scripts/synthesise.py "Your Topic Here"`

---

## 4. Maintenance & 2026 Optimisations

### **Cost Management**
- **Flash-Lite**: Always use `gemini-2.5-flash-lite` for ingestion to keep costs at ~$0.10/M tokens.
- **Batching**: The watcher is configured to run synthesis **once per batch**, saving 90% on synthesis costs for multiple uploads.
- **Caching**: `wiki_synthesis_cache.json` prevents paying for the same synthesis twice.

### **Security**
- **`.env`**: Never commit this file. It contains the `GEMINI_API_KEY` and DB credentials.
- **`.gitignore`**: Updated to protect the environment and Quartz build caches.

---

## 5. Future Roadmap
- [ ] **Phase 5 Completion**: Add project to `poovi.me` portfolio and record walkthrough.
- [ ] **GCS Integration**: Transition to the official Google Batch API for 50% extra discount on massive syntheses.
- [ ] **Semantic Pruning**: Refine the indexer to only send the top 20 most relevant pages during synthesis to avoid context window bloat.

---

**Curator**: Poovannan Rajendran  
**Architect**: Gemini CLI  
**Last Updated**: 2026-04-21
