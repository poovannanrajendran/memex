-- Migration 002: Add content_hash and wiki_slug tracking to ingested_files
ALTER TABLE ingested_files ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);
ALTER TABLE ingested_files ADD COLUMN IF NOT EXISTS wiki_slug TEXT;

CREATE INDEX IF NOT EXISTS idx_ingested_files_content_hash ON ingested_files(content_hash);
CREATE INDEX IF NOT EXISTS idx_ingested_files_wiki_slug ON ingested_files(wiki_slug);
