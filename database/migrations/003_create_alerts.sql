-- MIGRATION 003: Create alerts table
-- Run THIRD in Supabase SQL Editor
-- (references users.id — run migration 001 first)

CREATE TABLE IF NOT EXISTS alerts (
  id          SERIAL PRIMARY KEY,
  device_id   VARCHAR(50),
  zone        VARCHAR(100),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  sound_db    NUMERIC(5,2),
  vibration   NUMERIC(5,2),
  status      VARCHAR(20)      DEFAULT 'unresolved',
  resolved_by INTEGER          REFERENCES users(id),
  created_at  TIMESTAMPTZ      DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_status
  ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_time
  ON alerts(created_at DESC);
