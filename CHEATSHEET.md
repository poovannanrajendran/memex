# memex — Operator Cheat Sheet

## 📂 Data Ingestion (The Inbox)
Drop raw files into these folders on **automation-runner-01** at `/home/labadmin/memex/raw/`.

| Folder | Source Type | Supported Formats |
| :--- | :--- | :--- |
| `raw/articles/` | Article | `.md`, `.txt`, `.html` |
| `raw/pdfs/` | PDF | `.pdf` (Papers, Reports) |
| `raw/transcripts/`| Transcript | `.md`, `.txt` (Podcast, Meetings) |
| `raw/youtube/` | YouTube | `.json`, `.md` |
| `raw/posts/` | Post | `.md` (LinkedIn, Social) |
| `raw/openclaw/` | OpenClaw | `.md` (Agent Research) |

---

## 🛠️ CLI Commands (On Runner)
Run these from `/home/labadmin/memex/`.

### **General Maintenance**
- **Trigger Automation**: `./.venv/bin/python scripts/watcher.py`
- **Add URL Directly**: `./.venv/bin/python scripts/add_url.py "https://url.com"`
- **Manual Ingest**: `./.venv/bin/python scripts/ingest.py path/to/file.md`
- **Topic Synthesis**: `./.venv/bin/python scripts/synthesise.py "Topic String"`
- **Health Check**: `./.venv/bin/python scripts/lint.py`

### **Deployment & Logs**
- **Update Runner**: `git pull origin main`
- **Restart API**: `./scripts/deploy_api.sh`
- **View Cron Logs**: `tail -f /var/log/memex-watcher.log`
- **Check DB Stats**: `psql -d memex -c "SELECT * FROM pipeline_runs LIMIT 5;"`

---

## 🌐 Runner API (Port 8000)
Available on your local network at `http://192.168.1.30:8000`.
Requires Header: `Authorization: Bearer <RUNNER_API_SECRET>`

- **POST `/run`**: Triggers full watcher pipeline.
- **POST `/ingest`**: Ingest a specific path.
- **GET `/status`**: View last 5 pipeline runs.
- **GET `/search?q=query`**: Full-text search of the wiki index.
- **GET `/wiki/synthesis/list`**: List all synthesis reports.

---

## 🧠 Navigation & View
- **Public Wiki**: [https://memex.poovi.me](https://memex.poovi.me)
- **Local Browser**: Open `/Users/poovannanrajendran/Documents/GitHub/memex` in **Obsidian**.
- **Graph View**: `Cmd + G` in Obsidian.

---

## ⚡ 2026 Optimisation Keys
- **Cost**: ~$0.10 per 1M tokens (using **Flash-Lite**).
- **Batching**: Synthesis runs only **once per batch** of files.
- **Auto-Sync**: Every successful run **automatically pushes** to GitHub.
