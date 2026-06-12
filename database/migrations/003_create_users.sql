-- Run in Supabase SQL Editor (third)
-- Auth/passwords are handled by Supabase Auth.
-- This table stores profile/role data.
CREATE TABLE IF NOT EXISTS users (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(100),
  email      VARCHAR(100)  UNIQUE NOT NULL,
  role       VARCHAR(20)   DEFAULT 'ranger',
  created_at TIMESTAMPTZ   DEFAULT NOW()
);
