-- Run once against PostgreSQL if the ORM metadata was not auto-created.
-- Scheduled job moves rows from risk_history into this table.

CREATE TABLE IF NOT EXISTS risk_history_archive (
    id UUID PRIMARY KEY,
    risk_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    changed_by_id UUID NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL,
    previous_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_history_archive_changed_at ON risk_history_archive (changed_at);
CREATE INDEX IF NOT EXISTS idx_risk_history_archive_risk_id ON risk_history_archive (risk_id);
