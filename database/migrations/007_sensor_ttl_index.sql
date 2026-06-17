
-- MIGRATION 007: index to make the 9-minute TTL cleanup sweep fast.
-- Run in Supabase SQL Editor (or it's covered automatically by
-- `npx prisma db push` if you're using the Prisma schema, since the
-- index already exists there as idx_sr_time).
--
-- This is the manual-SQL equivalent fallback for the TTL cleanup query:
--   DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '9 minutes';

CREATE INDEX IF NOT EXISTS idx_sensor_readings_recorded_at
  ON sensor_readings (recorded_at);

-- Optional: enable pg_cron for a DB-side scheduled sweep as a second
-- layer of defense, independent of whether the Node backend is awake.
-- Uncomment if your Supabase project has pg_cron enabled
-- (Database -> Extensions -> pg_cron):
--
-- SELECT cron.schedule(
--   'smartforest_sensor_ttl_sweep',
--   '* * * * *',  -- every minute
--   $$DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '9 minutes'$$
-- );
