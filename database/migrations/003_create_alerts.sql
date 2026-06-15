-- MIGRATION 003: alerts table
-- Run THIRD in Supabase SQL Editor
-- Requires migration 001 (users) to exist first

-- alert_type:
--   'illegal_logging' = triggered by microphone detecting chainsaw sounds
--   'fire'            = triggered by flame sensor detecting fire/heat

CREATE TABLE IF NOT EXISTS alerts (
  id             SERIAL PRIMARY KEY,
  device_id      VARCHAR(50),
  sensor_type    VARCHAR(20)  DEFAULT 'microphone',
  alert_type     VARCHAR(30)  DEFAULT 'illegal_logging',
  zone           VARCHAR(100),
  latitude       DOUBLE PRECISION,
  longitude      DOUBLE PRECISION,
  -- Microphone reading that triggered alert
  sound_db       NUMERIC(5,2),
  -- Flame reading that triggered alert
  flame_detected BOOLEAN      DEFAULT FALSE,
  temperature_c  NUMERIC(5,2),
  -- Status
  status         VARCHAR(20)  DEFAULT 'unresolved',
  resolved_by    INTEGER      REFERENCES users(id),
  created_at     TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_status
  ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_time
  ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type
  ON alerts(alert_type);
