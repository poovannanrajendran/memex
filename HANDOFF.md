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
- **`watcher.py`**: Orchestrates the pipeline and now includes post-push webhooks for Qdrant sync.
- **`runner_api.py`**: FastAPI service extended with:
  - `/linkedin/post`: Direct publishing to Poovi's LinkedIn via n8n.
  - `/search`: Full-text keyword search across `wiki_index.json`.
  - `/wiki/{type}/{slug}`: Full content retrieval for agent context.
  - `/ingest`: Support for raw markdown write-backs from external agents.
- **`memex_mcp.py`**: Refactored to **FastMCP**. This stdio server allows OpenClaw agents to search Memex, retrieve synthesis lists, and post to LinkedIn directly from Telegram.

### **B. The Database & Vector Store**
- **PostgreSQL (`192.168.1.30`)**: Tracks runs, steps, and precise token/USD costs.
- **Qdrant (`192.168.1.20`)**: Vector store for semantic search. Incremental sync is triggered by the watcher via n8n.

### **C. The Public Wiki (Vercel)**
Deployed via **Quartz** to `memex.poovi.me`.
- **`probe_vercel.py`**: Ensures the deployment is successful before completing the watcher run.

---

## 3. Operational Guide

### **Standard Ingestion Loop**
1.  **Capture**: Drop a file into `raw/` or have an OpenClaw agent POST content to `/ingest`.
2.  **Wait**: Cron triggers `watcher.py` every 15 minutes.
3.  **Sync**: Watcher pushes to Git (triggering Vercel) and sends a webhook to n8n (updating Qdrant).
4.  **View**: Changes appear on `memex.poovi.me` and become searchable by OpenClaw agents.

### **Manual Controls**
- **Force Run**: `python3 scripts/watcher.py`
- **Bulk Vector Seed**: `python3 scripts/openclaw_ingest.py`
- **LinkedIn Post**: Use the `linkedin_post` tool via OpenClaw or POST to `/linkedin/post`.

---

## 4. Maintenance & 2026 Optimisations

### **Cost & Efficiency**
- **FastMCP**: Standardised tool interface for seamless multi-agent collaboration.
- **Incremental Sync**: Only new ingests are pushed to Qdrant, saving bandwidth and processing.
- **Flash-Lite**: Hardcoded for high-volume ingestion tasks to maintain extreme cost efficiency.

### **Security**
- **Bearer Auth**: All `runner_api` endpoints require the `RUNNER_API_SECRET` token.
- **MCP Security**: SSH forced commands restrict the OpenClaw user to execution of the MCP script only.

---

## 5. Future Roadmap
- [ ] **Phase 5 Polish**: Complete the public README and record the 3-minute walkthrough.
- [ ] **Deployment**: Perform `git pull` and `systemctl restart memex-runner` on `automation-runner-01` to activate new endpoints.
- [ ] **GCS Transition**: Move to Google Cloud Storage for permanent backup of the `raw/` directory.

---

**Curator**: Poovannan Rajendran  
**Architect**: Gemini CLI  
**Last Updated**: 2026-05-03
