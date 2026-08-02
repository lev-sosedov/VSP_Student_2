-- Apply with the user-service migration runner in a deployment window.
-- This migration is intentionally not applied automatically to the working DB.
CREATE TABLE user_event_outbox (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    event_type VARCHAR(64) NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    auth_id INTEGER NULL,
    payload TEXT NOT NULL,
    published_at TIMESTAMP NULL
);
CREATE INDEX ix_user_event_outbox_user_id ON user_event_outbox (user_id);
