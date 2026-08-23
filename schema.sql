-- Compass content pipeline control plane. SQLite. File: control.db

CREATE TABLE IF NOT EXISTS cycles (
    week_id       TEXT PRIMARY KEY,        -- ISO week, e.g. '2026-W35'
    status        TEXT NOT NULL DEFAULT 'open',
                  -- open | manual_pending | complete | archived
    opened_at     TEXT NOT NULL DEFAULT (datetime('now')),
    closed_at     TEXT,
    archived_at   TEXT
);

CREATE TABLE IF NOT EXISTS content_items (
    id                TEXT PRIMARY KEY,     -- '{week_id}-{platform}-{slug}'
    week_id           TEXT NOT NULL REFERENCES cycles(week_id),
    platform          TEXT NOT NULL,        -- site|linkedin|instagram|telegram|whatsapp|bale
    pillar            TEXT,                 -- diagnostic|collocation|markup|other
    post_date         TEXT NOT NULL,        -- ISO date
    post_time         TEXT,                 -- HH:MM local (Asia/Tehran), null = manual
    mode              TEXT NOT NULL,        -- manual|automated
    content_path      TEXT NOT NULL,        -- path to drafted content file, relative to repo root
    idempotency_key   TEXT NOT NULL UNIQUE, -- '{week_id}:{platform}:{post_date}'
    state             TEXT NOT NULL DEFAULT 'intake',
                      -- intake | pending_approval | approved | rejected
                      -- manual_pending | staged | posted | failed | archived
    approved_by       TEXT,
    approved_at       TEXT,
    scheduled_at      TEXT,
    posted_at         TEXT,
    notes             TEXT
);

CREATE INDEX IF NOT EXISTS idx_items_week  ON content_items(week_id);
CREATE INDEX IF NOT EXISTS idx_items_state ON content_items(state);
