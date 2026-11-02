# Pipeline ownership and confirmed semantic delivery

Standalone/API ingestion acquires the host-local pipeline lock, validates schema, registers the raw file, skips only a matching SHA-256, and records success/failure. It rebuilds both indexes before committing and pushing. Batch mode is explicit and leaves finalisation to its watcher parent. Tracking run IDs never imply ownership.

Migration 003 adds a durable latest-version delivery outbox. A source resolves through its recorded database wiki_slug, not filename/title guesses. Jobs store page bytes and a SHA-256. Unchanged documents remain idempotent; changed documents replace the pending job for that page. Network failures persist with exponential backoff capped at one hour. Delivery marks success only after Qdrant confirms `completed` with `wait=true`. Pending jobs are retried by idle watcher runs too. A pipeline run with incomplete delivery is reported failed rather than silently successful.

The existing loopback Ollama model `nomic-embed-text:latest` is reached through an authenticated embedding-only bridge on AI VM port 11435. The bridge exposes no generation endpoint and accepts no other model. Document inputs use `search_document:`; queries use `search_query:`. Vectors must be 768-dimensional, finite and nonzero. Qdrant payloads include model identity, dimensions and content hash. The dedicated collection is `memex-knowledge-768d`; existing payload collections are preserved.

Embeddings currently use title and the first 6,000 characters of a page; Ollama may additionally truncate at model context length. Payloads retain the complete page. This is document-level retrieval, not exhaustive chunk-level retrieval.

## Operations

Apply migrations 002 and 003 before starting the new code. Set private bridge token and MEMEX_EMBED_URL in the runner environment; .env.example documents names without secrets.

Run commands from the repository as its service user:

```sh
.venv/bin/python -m scripts.delivery --limit 100
.venv/bin/python -m scripts.delivery --enqueue-index --limit 100
.venv/bin/python -m scripts.repair_source_mappings
```

The delivery CLI and repair CLI acquire the same pipeline lock. Bulk embedding uses the existing local model and does not call Gemini. Inspect `delivery_outbox` for status, attempts, last_error and next_attempt_at. A pending job is not a completed delivery.

Authenticated `GET /semantic-search?q=...&limit=5` queries the dedicated collection using the same embedding model. Existing `/search` remains lexical and refreshes its cached index when the index file changes.

Historical missing summaries can be recovered as explicitly labelled `raw_source_only` pages. The original hidden `.md` page is preserved and copied to a nonempty slug. New non-Latin-only names use deterministic hashes instead of empty filenames. No replacement AI summaries are invented.

`deploy_n8n_embedding.py` is an administrative deployment helper using n8n's supported export/import/publish CLI. It adds a real local embedding HTTP node and rejects zero vectors in the existing webhook workflow. It never reads n8n API keys from the database. The main Memex pipeline delivers directly through its durable outbox; it does not trigger Telegram during ingestion verification.

Rollback: stop the new worker/service, restore the pre-change app and private environment backup, restart the previous daemon and restore the saved crontab. Migration 003 is additive and may remain in place. Do not delete original Qdrant collections or restore an old database over new successful records without first preserving current state.

The bridge systemd template is in `deploy/memex-embedding.service`. Install its Python script under `/opt/memex-embedding`, store token and bind address in root-readable `/etc/memex-embedding.env`, and permit TCP 11435 only from automation runner 192.168.1.30 to AI VM 192.168.1.24. The service uses a transient systemd user. Do not expose the loopback Ollama generation endpoint.
