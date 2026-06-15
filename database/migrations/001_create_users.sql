-- MIGRATION 001: users table
-- Run FIRST in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS users (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(100),
  email      VARCHAR(100)  UNIQUE NOT NULL,
  role       VARCHAR(20)   DEFAULT 'ranger',
  created_at TIMESTAMPTZ   DEFAULT NOW()
);
