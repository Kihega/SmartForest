-- DEV SEED: Sample data for local testing
-- Run AFTER all 3 migrations in Supabase SQL Editor

INSERT INTO users (name, email, role) VALUES
  ('Admin Ranger', 'admin@smartforest.tz', 'admin'),
  ('John Ranger',  'john@smartforest.tz',  'ranger')
ON CONFLICT (email) DO NOTHING;

INSERT INTO sensor_readings
  (device_id, zone, latitude, longitude, sound_db, vibration, is_alert)
VALUES
  ('SENSOR-001', 'Kibiti-North', -7.72,  38.95, 45.2, 2.1, FALSE),
  ('SENSOR-002', 'Kibiti-South', -7.85,  38.88, 91.5, 8.3, TRUE),
  ('SENSOR-003', 'Kibiti-East',  -7.78,  39.05, 33.0, 1.5, FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO alerts
  (device_id, zone, latitude, longitude, sound_db, vibration, status)
VALUES
  ('SENSOR-002', 'Kibiti-South', -7.85, 38.88, 91.5, 8.3, 'unresolved')
ON CONFLICT DO NOTHING;
