-- MIGRATION 006: add phone column to users table (OPTIONAL)
-- Run in Supabase SQL Editor only when you want phone stored in the DB.
-- By default phone is stored in Supabase user_metadata (no DB column needed).
--
-- After running this SQL, also:
--   1. Uncomment phone field in backend/prisma/schema.prisma
--   2. Run: npx prisma db push

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS phone VARCHAR(30);
