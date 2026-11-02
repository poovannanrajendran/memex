CREATE TABLE IF NOT EXISTS delivery_outbox (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID REFERENCES pipeline_runs(run_id),
    slug TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'delivered')),
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (slug)
);
CREATE INDEX IF NOT EXISTS delivery_outbox_pending ON delivery_outbox(next_attempt_at)
    WHERE status = 'pending';
