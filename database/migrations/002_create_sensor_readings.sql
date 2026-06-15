-- MIGRATION 002: sensor_readings table
-- Run SECOND in Supabase SQL Editor

-- sensor_type:
--   'microphone' = detects abnormal sounds (chainsaw noise -> illegal logging)
--   'flame'      = detects fire/heat signatures in forest areas

CREATE TABLE IF NOT EXISTS sensor_readings (
  id          SERIAL PRIMARY KEY,
  device_id   VARCHAR(50)      NOT NULL,
  sensor_type VARCHAR(20)      NOT NULL DEFAULT 'microphone',
  zone        VARCHAR(100),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  -- Microphone sensor fields
  sound_db    NUMERIC(5,2),
  -- Flame sensor fields
  flame_detected  BOOLEAN      DEFAULT FALSE,
  temperature_c   NUMERIC(5,2),
  -- Alert flag
  is_alert    BOOLEAN          DEFAULT FALSE,
  recorded_at TIMESTAMPTZ      DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sr_device
  ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sr_time
  ON sensor_readings(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_sr_type
  ON sensor_readings(sensor_type);
