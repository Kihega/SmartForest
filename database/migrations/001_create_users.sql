-- MIGRATION 001: Create users table
-- Run this FIRST in Supabase SQL Editor
-- (alerts table references users.id so users must exist first)

CREATE TABLE IF NOT EXISTS users (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(100),
  email      VARCHAR(100)  UNIQUE NOT NULL,
  role       VARCHAR(20)   DEFAULT 'ranger',
  created_at TIMESTAMPTZ   DEFAULT NOW()
);
