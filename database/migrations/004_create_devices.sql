-- MIGRATION 004: devices table
-- Run FOURTH in Supabase SQL Editor (after users migration)

CREATE TABLE IF NOT EXISTS devices (
  id          SERIAL PRIMARY KEY,
  device_id   VARCHAR(50)   UNIQUE NOT NULL,
  owner_id    INTEGER       REFERENCES users(id) ON DELETE SET NULL,
  zone        VARCHAR(100),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  active      BOOLEAN       DEFAULT TRUE,
  last_seen   TIMESTAMPTZ,
  created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_owner
  ON devices(owner_id);
CREATE INDEX IF NOT EXISTS idx_devices_active
  ON devices(active);

-- Update last_seen when sensor data arrives for this device
-- (called from application layer via patch /devices/:id/status or MQTT handler)
