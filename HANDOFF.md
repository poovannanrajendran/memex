# memex — Handoff Document

## 📍 Project Status: **Phase 4 Complete (Autonomous State)**
The **memex** project has transitioned from a manual tool into a production-grade, autonomous intelligence engine. It is now running headlessly on your homelab infrastructure.

---

## 🏗️ Technical Architecture
### **1. Core Infrastructure**
- **Server**: `automation-runner-01` (`192.168.1.30`)
- **User**: `codex_agent_agent`
- **Working Directory**: `/home/codex_agent_agent/memex`
- **Virtual Environment**: `/home/codex_agent_agent/memex/venv/bin/python3`

### **2. Automation Pipeline**
- **Trigger**: Hourly Cron Job at **:18** past each hour.
- **Logic**: `scripts/youtube_watcher.py`
    - Queries PostgreSQL (`192.168.1.20`) for new liked videos.
    - Processes delta records (unprocessed only).
    - Tiered Extraction: Transcript -> Description (Usable prose fallback).
    - Title Escaping: Automatic YAML-safe title formatting.
    - Interconnectivity: Automated stub creation for all related concepts.
- **AI Backend**: **Gemini 2.5 Flash Lite** via Google Generative AI SDK.
- **Output**: Automatic Git commits + `git push` to GitHub `main`.

### **3. Wiki Composition**
- **Size**: ~7,000 interlinked Markdown pages.
- **Health**: 0 broken wikilinks, 0 missing index entries.
- **Static Site**: Deployed via **Quartz 4** on Vercel (`memex-poovi.vercel.app`).
    - Note: Vercel configuration now supports **Clean URLs** and fixed asset resolution for subpages.

---

## ⚡ Key Achievements
- **The 36p Bulk Ingest**: Successfully processed **770+ unique YouTube videos** (years of history) in a single run. Total API cost: **£0.36**.
- **Model Prowess**: Proved the dominance of Gemini Flash models for lightning-fast processing with massive 1M+ token context windows at fractional costs.

---

## 🛠️ Operational Commands
### **Manual Sync from Server**
If automation fails to push (auth reset):
```bash
ssh automation-runner-01 "cd ~/memex && git push origin master:main"
```

### **Run Manual Ingestion Batch**
To force a run of 10 videos:
```bash
ssh automation-runner-01 "cd ~/memex && ./venv/bin/python3 scripts/youtube_watcher.py 10"
```

### **Update Site Index**
```bash
python3 scripts/indexer.py && python3 scripts/rebuild_index_md.py
```

---

## 🚧 Next Steps (Phase 5)
- **Portfolio Polish**: Refine the visual layout of the index page.
- **Walkthrough**: Record a 3-minute video showing the transition from a "YouTube Like" to a "Wiki Concept Page" automatically.
- **Public Launch**: Final README cleanup and repo visibility toggle.

---
**Librarian Status**: Autonomous & Vigilant.
**Sync Status**: All environments (MacBook, Server, GitHub) are 100% aligned.
