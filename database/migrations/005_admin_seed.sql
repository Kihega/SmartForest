-- MIGRATION 005: seed first admin user in the users table
-- NOTE: You must also create this user in Supabase Auth dashboard
--       (or via the Supabase CLI: supabase auth create-user)
--       Email: admin@smartforest.tz   Password: Admin@SmartForest2026

INSERT INTO users (name, email, role) VALUES
  ('System Admin', 'admin@smartforest.tz', 'admin')
ON CONFLICT (email) DO UPDATE SET role = 'admin';
