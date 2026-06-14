-- MIGRATION 002: Create sensor_readings table
-- Run SECOND in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS sensor_readings (
  id          SERIAL PRIMARY KEY,
  device_id   VARCHAR(50)      NOT NULL,
  zone        VARCHAR(100),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  sound_db    NUMERIC(5,2),
  vibration   NUMERIC(5,2),
  is_alert    BOOLEAN          DEFAULT FALSE,
  recorded_at TIMESTAMPTZ      DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_device
  ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_time
  ON sensor_readings(recorded_at DESC);
