'use strict';
/**
 * Jest global setup — mocks every external dependency so tests run
 * without a live database, MQTT broker, or Supabase project.
 *
 * Mocking strategy:
 *   - PrismaClient  → all model methods return sensible defaults
 *   - db (pg pool)  → query() returns { rows:[], rowCount:0 }
 *   - supabase      → auth methods return success mocks
 *   - mqtt          → no-op client
 *   - userModel     → direct mock (avoids Prisma/pg in auth tests)
 */

// ── Prisma ────────────────────────────────────────────────────────────────
const mockPrisma = {
  user: {
    findUnique  : jest.fn().mockResolvedValue(null),
    findMany    : jest.fn().mockResolvedValue([]),
    create      : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    upsert      : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    update      : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    delete      : jest.fn().mockResolvedValue({}),
    count       : jest.fn().mockResolvedValue(0),
  },
  alert: {
    findUnique  : jest.fn().mockResolvedValue(null),
    findMany    : jest.fn().mockResolvedValue([]),
    create      : jest.fn().mockResolvedValue({ id:1, deviceId:'DEV-001', status:'unresolved', createdAt:new Date() }),
    createMany  : jest.fn().mockResolvedValue({ count:0 }),
    update      : jest.fn().mockResolvedValue({ id:1, status:'resolved', createdAt:new Date() }),
    count       : jest.fn().mockResolvedValue(0),
    deleteMany  : jest.fn().mockResolvedValue({ count:0 }),
  },
  sensorReading: {
    findUnique  : jest.fn().mockResolvedValue(null),
    findMany    : jest.fn().mockResolvedValue([]),
    findFirst   : jest.fn().mockResolvedValue(null),
    create      : jest.fn().mockResolvedValue({ id:1, deviceId:'DEV-001', isAlert:false, recordedAt:new Date() }),
    deleteMany  : jest.fn().mockResolvedValue({ count:0 }),
  },
  device: {
    findUnique  : jest.fn().mockResolvedValue(null),
    findMany    : jest.fn().mockResolvedValue([]),
    create      : jest.fn().mockResolvedValue({ id:1, deviceId:'smt-01a', active:true, createdAt:new Date() }),
    update      : jest.fn().mockResolvedValue({ id:1, deviceId:'smt-01a', active:false, createdAt:new Date() }),
    updateMany  : jest.fn().mockResolvedValue({ count:1 }),
    delete      : jest.fn().mockResolvedValue({}),
    count       : jest.fn().mockResolvedValue(0),
  },
  $disconnect : jest.fn().mockResolvedValue(undefined),
  $connect    : jest.fn().mockResolvedValue(undefined),
};

jest.mock('./src/config/prisma', () => mockPrisma);

// ── pg pool ───────────────────────────────────────────────────────────────
jest.mock('./src/config/db', () => ({
  query  : jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
  execute: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
  pool   : { query: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }) },
}));

// ── Supabase ──────────────────────────────────────────────────────────────
jest.mock('./src/config/supabase', () => ({
  auth: {
    signInWithPassword: jest.fn().mockResolvedValue({
      data: {
        user: {
          id: 'supabase-uid-123',
          email: 'test@example.com',
          user_metadata: { name: 'Test User', role: 'ranger' },
        },
        session: {
          access_token: 'mock-token-xyz',
          expires_at  : Math.floor(Date.now() / 1000) + 3600,
        },
      },
      error: null,
    }),
    signUp: jest.fn().mockResolvedValue({
      data: { user: { id: 'new-uid', email: 'new@example.com' } },
      error: null,
    }),
    signOut : jest.fn().mockResolvedValue({ error: null }),
    getUser : jest.fn().mockResolvedValue({
      data: { user: { id: 'supabase-uid-123', email: 'test@example.com' } },
      error: null,
    }),
    updateUser: jest.fn().mockResolvedValue({ error: null }),
    admin: {
      createUser: jest.fn().mockResolvedValue({
        data: { user: { id: 'admin-uid', email: 'newadmin@example.com' } },
        error: null,
      }),
    },
  },
}));

// ── userModel (direct mock — keeps auth tests simple) ─────────────────────
jest.mock('./src/models/userModel', () => ({
  create     : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getByEmail : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getById    : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getAll     : jest.fn().mockResolvedValue([]),
  updateRole : jest.fn().mockResolvedValue({ id:1, role:'admin' }),
  delete     : jest.fn().mockResolvedValue(undefined),
}));

// ── MQTT ──────────────────────────────────────────────────────────────────
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on         : jest.fn(),
    subscribe  : jest.fn(),
    publish    : jest.fn(),
    disconnect : jest.fn(),
  }),
}));

// ── Suppress console noise ────────────────────────────────────────────────
global.console.error = jest.fn();
global.console.warn  = jest.fn();
