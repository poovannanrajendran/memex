# TASKS.md — Second Brain Build Plan

> KISS: no ceremonies, no sprint planning, no story points.
> Work through phases in order. Tick tasks as done. Commit after each.

---

## Phase 1 — Fork and run ✅
**Goal:** A working vault with Gemini CLI driving real ingestion within one session.

- [x] Fork `NicholasSpisak/second-brain` to your GitHub account
- [x] Clone locally
- [x] Install Gemini CLI
- [x] Install the skills
- [x] Run the setup wizard inside Gemini CLI: type `/second-brain`
- [x] Copy `GEMINI.md` into the vault root
- [x] Initialise Git tracking on the vault
- [x] Install Obsidian and open the vault folder as a vault
- [x] Drop 3–5 test sources into `raw/`
- [x] Run `/second-brain-ingest` on each source and verify wiki pages are created
- [x] Confirm `wiki/index.md` and `wiki/log.md` are populated
- [x] Browse the Obsidian graph view — verify wikilinks are rendering

**Done when:** Three sources ingested, graph view shows linked pages, Git history shows one commit per ingest.

---

## Phase 2 — YouTube database integration ✅
**Goal:** Pipe the existing YouTube liked-video database into the vault as a first-class source type.

- [x] Export the YouTube liked-video database to a flat JSON file (Used CSV/JSON samples)
- [x] Write `scripts/youtube_to_raw.py`
- [x] Run the script: `python scripts/youtube_to_raw.py`
- [x] Batch-ingest the YouTube records: `/second-brain-ingest raw/youtube/`
- [x] Run `/second-brain-lint` — fix any broken wikilinks or missing index entries
- [x] Verify the Obsidian graph now shows YouTube-sourced entity pages connecting to concept pages

**Done when:** All YouTube records are ingested, speaker and concept pages exist, graph is populated.

---

## Phase 3 — Gemini API pipeline ✅
**Goal:** Move ingestion from interactive CLI to a Python script calling the Gemini API directly.

- [x] Install the Python SDK: `pip install google-genai`
- [x] Create `scripts/ingest.py`
- [x] Create `scripts/lint.py`
- [x] Test both scripts on new sources
- [x] Add `requirements.txt` with pinned dependencies
- [x] Add a `.env.example` with `GEMINI_API_KEY=`

**Done when:** Ingestion runs headlessly via `python scripts/ingest.py raw/articles/` without touching Gemini CLI.

---

## Phase 4 — Staleness detection and synthesis ✅
**Goal:** The wiki maintains itself — stale pages are flagged, cross-source synthesis is generated.

- [x] Add staleness detection to `scripts/lint.py` (Pending Search Grounding reset)
- [x] Build `/second-brain-synthesise` as a Python script `scripts/synthesise.py`
- [x] Run synthesis on cross-cutting topics:
  - [x] AI agent workflow design patterns
- [x] Schedule weekly lint as a cron job

**Done when:** At least three synthesis pages exist, lint runs automatically.

---

## Phase 5 — Portfolio polish 🏗️
**Goal:** The project is interview-ready and publicly demonstrable.

- [ ] Write a clean `README.md`
- [ ] Export a static snapshot of the wiki
- [ ] Record a 3-minute walkthrough video
- [ ] Add the project to `poovi.me` portfolio page
- [ ] Push the repo public

**Done when:** README is complete, repo is public, walkthrough video is recorded.
