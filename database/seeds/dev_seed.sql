-- DEV SEED: Sample data for testing
-- Run AFTER all 3 migrations in Supabase SQL Editor

INSERT INTO users (name, email, role) VALUES
  ('Admin Ranger', 'admin@smartforest.tz', 'admin'),
  ('John Ranger',  'john@smartforest.tz',  'ranger')
ON CONFLICT (email) DO NOTHING;

-- Microphone sensor readings (chainsaw detection)
INSERT INTO sensor_readings
  (device_id, sensor_type, zone, latitude, longitude,
   sound_db, is_alert)
VALUES
  ('MIC-001', 'microphone', 'Kibiti-North', -7.72, 38.95, 42.5, FALSE),
  ('MIC-002', 'microphone', 'Kibiti-South', -7.85, 38.88, 91.5, TRUE),
  ('MIC-003', 'microphone', 'Kibiti-East',  -7.78, 39.05, 33.0, FALSE)
ON CONFLICT DO NOTHING;

-- Flame sensor readings (fire detection)
INSERT INTO sensor_readings
  (device_id, sensor_type, zone, latitude, longitude,
   flame_detected, temperature_c, is_alert)
VALUES
  ('FLAME-001', 'flame', 'Kibiti-North', -7.72, 38.95, FALSE, 28.5, FALSE),
  ('FLAME-002', 'flame', 'Kibiti-South', -7.85, 38.88, TRUE,  67.3, TRUE)
ON CONFLICT DO NOTHING;

-- Alerts
INSERT INTO alerts
  (device_id, sensor_type, alert_type, zone,
   latitude, longitude, sound_db, status)
VALUES
  ('MIC-002', 'microphone', 'illegal_logging',
   'Kibiti-South', -7.85, 38.88, 91.5, 'unresolved');

INSERT INTO alerts
  (device_id, sensor_type, alert_type, zone,
   latitude, longitude, flame_detected, temperature_c, status)
VALUES
  ('FLAME-002', 'flame', 'fire',
   'Kibiti-South', -7.85, 38.88, TRUE, 67.3, 'unresolved');
