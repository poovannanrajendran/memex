-- memex Automation Engine Migration 001
-- Targets: pipeline tracking, file deduplication, and AI audit logging

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Table 1: pipeline_runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              SERIAL PRIMARY KEY,
    run_id          UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    triggered_by    VARCHAR(20) NOT NULL CHECK (triggered_by IN ('watcher', 'api', 'manual')),
    trigger_source  VARCHAR(100),          -- e.g. 'openclaw', 'curl', 'n8n', 'telegram'
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running', 'completed', 'failed', 'no_work')),
    files_found     INTEGER DEFAULT 0,
    files_processed INTEGER DEFAULT 0,
    files_skipped   INTEGER DEFAULT 0,
    files_failed    INTEGER DEFAULT 0,
    error_message   TEXT
);

-- Table 2: ingested_files
CREATE TABLE IF NOT EXISTS ingested_files (
    id                  SERIAL PRIMARY KEY,
    run_id              UUID NOT NULL REFERENCES pipeline_runs(run_id),
    file_path           TEXT NOT NULL,
    file_name           TEXT NOT NULL,
    source_type         VARCHAR(20) CHECK (source_type IN ('article', 'pdf', 'transcript', 'youtube', 'post', 'unknown')),
    file_size_bytes     INTEGER,
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingested_at         TIMESTAMPTZ,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped')),
    wiki_pages_created  INTEGER DEFAULT 0,
    wiki_pages_updated  INTEGER DEFAULT 0,
    entities_extracted  INTEGER DEFAULT 0,
    concepts_extracted  INTEGER DEFAULT 0,
    error_message       TEXT,
    UNIQUE(file_path)   -- prevents double-processing
);

-- Table 3: pipeline_steps
CREATE TABLE IF NOT EXISTS pipeline_steps (
    id              SERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES pipeline_runs(run_id),
    file_id         INTEGER REFERENCES ingested_files(id),  -- NULL for global steps
    step_name       VARCHAR(30) NOT NULL CHECK (step_name IN ('detect', 'ingest', 'lint', 'synthesise', 'git_commit')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    status          VARCHAR(20) NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running', 'completed', 'failed', 'skipped')),
    output_summary  TEXT,
    error_message   TEXT
);

-- Table 4: ai_calls
CREATE TABLE IF NOT EXISTS ai_calls (
    id                  SERIAL PRIMARY KEY,
    run_id              UUID NOT NULL REFERENCES pipeline_runs(run_id),
    file_id             INTEGER REFERENCES ingested_files(id),  -- NULL for lint/synthesise
    step_name           VARCHAR(30) NOT NULL,
    model               VARCHAR(50) NOT NULL,  -- 'gemini-2.5-pro' or 'gemini-2.5-flash'
    operation           VARCHAR(50) NOT NULL,  -- 'ingest_document', 'lint_check', 'synthesise', etc.
    input_tokens        INTEGER,
    output_tokens       INTEGER,
    total_tokens        INTEGER GENERATED ALWAYS AS (COALESCE(input_tokens,0) + COALESCE(output_tokens,0)) STORED,
    estimated_cost_usd  NUMERIC(10, 6),
    called_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms         INTEGER,
    success             BOOLEAN NOT NULL DEFAULT TRUE,
    error_message       TEXT
);

-- Table 5: ai_call_summary
CREATE TABLE IF NOT EXISTS ai_call_summary (
    id                      SERIAL PRIMARY KEY,
    run_id                  UUID NOT NULL UNIQUE REFERENCES pipeline_runs(run_id),
    total_calls             INTEGER DEFAULT 0,
    pro_calls               INTEGER DEFAULT 0,
    flash_calls             INTEGER DEFAULT 0,
    total_input_tokens      INTEGER DEFAULT 0,
    total_output_tokens     INTEGER DEFAULT 0,
    total_tokens            INTEGER DEFAULT 0,
    estimated_cost_usd      NUMERIC(10, 6) DEFAULT 0,
    generated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
