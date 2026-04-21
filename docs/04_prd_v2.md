# memex — PRD v2 (Optimised Automation Engine)

## 1. Product Summary
**memex** v2 transforms the system from an interactive tool into an autonomous enterprise-grade automation engine. It introduces a structured data layer for auditability and a multi-tiered synthesis strategy to reduce API costs by up to 75%.

## 2. Technical Delta (Improvements over v1)

| Feature | PRD v1 (MVP) | PRD v2 (Optimised) |
| :--- | :--- | :--- |
| **Persistence** | None (Local files only) | **PostgreSQL**: Full pipeline audit trail. |
| **Deduplication** | Manual check | **SQL UNIQUE Index**: Automatic file deduplication. |
| **Cost Control** | None (Full wiki load) | **Index-based Filtering**: Only loads relevant context. |
| **Reasoning** | Single model | **Model Routing**: Flash-Lite for Extraction, Pro for Synthesis. |
| **Interactivity** | CLI-only | **REST API**: Triggers via OpenClaw, n8n, or Telegram. |
| **Synthesis** | Continuous | **Batch Synthesis**: Runs once per run, not per file. |

## 3. New Requirements (v2)

### 3.1 Automated Watcher
- Continuous monitoring of the `raw/` directory via `watcher.py`.
- Automated detection of new source files with type inference (article, pdf, youtube, etc.).

### 3.2 Structured Logging & Auditing
- Log every pipeline run, step, and individual AI API call to PostgreSQL.
- Track token usage (input/output) and estimate USD costs using 2026 pricing.
- Store results of extraction (pages created, entities found) for analytics.

### 3.3 Synthesis Cost Optimisation
- **Wiki Indexing**: Maintain a `wiki_index.json` metadata cache for sub-millisecond relevance scoring.
- **Claim Extraction**: Extract 3-5 key claims from wiki pages using cheap models (Flash-Lite) before sending to high-reasoning models (Pro).
- **Caching**: Skip re-synthesis if the topic and the state of the relevant wiki pages have not changed.

### 3.4 API Gateway
- Provide a FastAPI-based runner for external systems.
- Endpoints for `/run`, `/ingest`, and `/status`.
- Bearer-token authentication for security.

## 4. Current State Architecture (Standalone)

### 4.1 The Loop
1.  **Poll**: `watcher.py` finds `risk_report_2026.pdf`.
2.  **Filter**: `register_file` checks PostgreSQL; proceeds if new.
3.  **Ingest**: `ingest.py` (via Flash-Lite) extracts data into Markdown.
4.  **Index**: `indexer.py` updates the JSON metadata cache.
5.  **Synthesise**: `synthesise.py` (via Pro) updates cross-source reports.
6.  **Audit**: Pipeline run summary written to DB; Git commit pushed.

## 5. Performance Targets
- **Input Token Reduction**: 70% decrease in tokens sent to high-tier models.
- **Cost per Synthesis**: < $0.40 USD (from $1.25 baseline).
- **Cache Hit Latency**: < 100ms for repeated queries.
