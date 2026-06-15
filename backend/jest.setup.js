// jest.setup.js
// Runs before every test file.
// Mocks external services so tests never need a live DB or Supabase.

// ── Mock pg Pool (Supabase PostgreSQL) ──────────────────
jest.mock('./src/config/db', () => {
  return {
    query: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
  };
});

// ── Mock Supabase client ─────────────────────────────────
jest.mock('./src/config/supabase', () => {
  return {
    auth: {
      signInWithPassword: jest.fn().mockResolvedValue({
        data: null,
        error: { message: 'Invalid credentials' },
      }),
      signOut: jest.fn().mockResolvedValue({ error: null }),
      getUser: jest.fn().mockResolvedValue({
        data: null,
        error: { message: 'Invalid token' },
      }),
    },
  };
});

// ── Mock MQTT (no broker needed in tests) ────────────────
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on         : jest.fn(),
    subscribe  : jest.fn(),
    publish    : jest.fn(),
    disconnect : jest.fn(),
  }),
}));
