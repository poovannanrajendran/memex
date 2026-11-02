# Changelog

All notable changes to **Poovi's Second Brain (Memex)** are documented in this file.

## [v1.1.0] - 2026-11-02

### Architecture & Pipeline Hardening
- **Host-Local Process Locking:** Integrated `pipeline_lock` (`fcntl.flock`) across `watcher.py`, `scripts/ingest.py`, and `scripts/runner_api.py` (`POST /run`, `POST /ingest`). Prevents overlapping cron jobs and API-triggered workers from corrupting state or executing concurrent runs.
- **Strict SHA-256 Deduplication:** Raw source deduplication uses content SHA-256 hashes instead of file size or modified timestamps. Eliminated runaway re-ingestion loops.
- **Circuit Breaker:** Implemented spend-cap detection on Google GenAI SDK calls. If a project monthly cap is reached, remaining queues and downstream synthesis are aborted immediately rather than cycling through fallback models.
- **Two-Stage Batch Indexing:** Preliminary index rebuild occurs after source ingestion so batch linting and batch synthesis can access new pages; final index rebuild occurs post-synthesis.
- **Atomic Cache Operations:** Refactored `synthesis_cache.py` with content-byte hashing and atomic filesystem writes (`.tmp` + `os.replace`), fixing JSON corruption on concurrent or interrupted operations.
- **Grounding & FinOps Safety:** Gated search grounding in `scripts/lint.py` behind the explicit `--grounding` flag with a default cap of 5 checks per invocation and full logging into the PostgreSQL `ai_calls` table.

### Semantic Search & Delivery Outbox
- **Local Embedding Bridge:** Configured private authenticated bridge on `192.168.1.24:11435` proxying `nomic-embed-text:latest`. Fully eliminates commercial API costs for embedding generation.
- **Dedicated 768D Qdrant Collection:** Created `memex-knowledge-768d` with valid 768-dimensional vectors. Preserved existing 4D `memex-knowledge` collection.
- **PostgreSQL Delivery Outbox:** Added migration `003_delivery_outbox.sql` providing durable, idempotent delivery with exponential backoff and automatic retry during watcher runs.
- **Semantic Search Endpoint:** Added authenticated `GET /semantic-search?q=...&limit=5` in `runner_api.py` querying `memex-knowledge-768d`.

### Data Recovery & Fixes
- **Unicode Slugification:** Fixed empty slug generation for non-Latin titles (e.g. Tamil titles), preventing overwrite collisions on `wiki/sources/.md`.
- **Source Slug Mapping:** Explicit `wiki_slug` column tracked in `ingested_files` via migration `002_add_content_hash_and_wiki_slug.sql`, resolving 104/104 active raw sources cleanly.
