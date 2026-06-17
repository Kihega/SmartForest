
-- MIGRATION 005 : Seed admin and ranger users
-- Fallback SQL if Prisma seed (npx prisma db seed) fails.
--
-- These rows are the DB profile records only.
-- Supabase Auth accounts must be created separately via:
--   npx prisma db seed          (recommended — creates Auth + DB)
--   OR: Supabase Auth dashboard (Authentication > Users > Add user)
--
-- Credentials: admin@smf.tz / smf@1234   ranger@smf.tz / smf@1234

INSERT INTO users (name, email, role) VALUES
  ('System Admin', 'admin@smf.tz',  'admin'),
  ('Field Ranger', 'ranger@smf.tz', 'customer')
ON CONFLICT (email) DO UPDATE
  SET name = EXCLUDED.name,
      role = EXCLUDED.role;
