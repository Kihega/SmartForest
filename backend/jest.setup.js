'use strict';
/**
 * Jest global setup — mocks every external dependency.
 * No live DB, MQTT broker, or Supabase project required.
 *
 * Mock inventory:
 *   prisma        → all model methods with sensible return values
 *   db (pg pool)  → query() returns { rows:[], rowCount:0 }
 *   supabase      → auth methods return success stubs
 *   userModel     → direct mock (decouples auth/admin/devices routes)
 *   deviceModel   → direct mock (decouples devices route)
 *   alertModel    → direct mock (decouples alerts route)
 *   sensorModel   → direct mock (decouples sensors route)
 *   mqtt          → no-op client
 */

// ── Prisma singleton ─────────────────────────────────────────────────────────
const mockPrisma = {
  user: {
    findUnique : jest.fn().mockResolvedValue(null),
    findMany   : jest.fn().mockResolvedValue([]),
    create     : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    upsert     : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    update     : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test', createdAt:new Date() }),
    delete     : jest.fn().mockResolvedValue({}),
    count      : jest.fn().mockResolvedValue(0),
  },
  alert: {
    findUnique : jest.fn().mockResolvedValue(null),
    findMany   : jest.fn().mockResolvedValue([]),
    findFirst  : jest.fn().mockResolvedValue(null),
    create     : jest.fn().mockResolvedValue({ id:1, deviceId:'DEV-001', status:'unresolved', createdAt:new Date() }),
    createMany : jest.fn().mockResolvedValue({ count:0 }),
    update     : jest.fn().mockResolvedValue({ id:1, status:'resolved', createdAt:new Date() }),
    count      : jest.fn().mockResolvedValue(0),
    deleteMany : jest.fn().mockResolvedValue({ count:0 }),
  },
  sensorReading: {
    findUnique : jest.fn().mockResolvedValue(null),
    findMany   : jest.fn().mockResolvedValue([]),
    findFirst  : jest.fn().mockResolvedValue(null),
    create     : jest.fn().mockResolvedValue({ id:1, deviceId:'DEV-001', isAlert:false, recordedAt:new Date() }),
    deleteMany : jest.fn().mockResolvedValue({ count:0 }),
  },
  device: {
    findUnique : jest.fn().mockResolvedValue(null),
    findMany   : jest.fn().mockResolvedValue([]),
    findFirst  : jest.fn().mockResolvedValue(null),
    create     : jest.fn().mockResolvedValue({ id:1, deviceId:'smt-01a', active:true, createdAt:new Date() }),
    update     : jest.fn().mockResolvedValue({ id:1, deviceId:'smt-01a', active:false, createdAt:new Date() }),
    updateMany : jest.fn().mockResolvedValue({ count:1 }),
    delete     : jest.fn().mockResolvedValue({}),
    count      : jest.fn().mockResolvedValue(0),
  },
  $disconnect : jest.fn().mockResolvedValue(undefined),
  $connect    : jest.fn().mockResolvedValue(undefined),
};
jest.mock('./src/config/prisma', () => mockPrisma);

// ── pg pool ──────────────────────────────────────────────────────────────────
jest.mock('./src/config/db', () => ({
  query  : jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
  execute: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
}));

// ── Supabase ─────────────────────────────────────────────────────────────────
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
    signOut   : jest.fn().mockResolvedValue({ error: null }),
    getUser   : jest.fn().mockResolvedValue({
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

// ── userModel — mocked directly so routes don't touch Prisma/pg ──────────────
// Default: role:'ranger'  (non-admin user)
// Override per-test with: userModel.getByEmail.mockResolvedValueOnce(...)
jest.mock('./src/models/userModel', () => ({
  create     : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getByEmail : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getById    : jest.fn().mockResolvedValue({ id:1, email:'test@example.com', role:'ranger', name:'Test User' }),
  getAll     : jest.fn().mockResolvedValue([{ id:1, email:'test@example.com', role:'ranger', name:'Test User' }]),
  updateRole : jest.fn().mockResolvedValue({ id:1, role:'admin' }),
  delete     : jest.fn().mockResolvedValue(undefined),
}));

// ── deviceModel — mocked directly so devices route doesn't touch Prisma/pg ───
jest.mock('./src/models/deviceModel', () => ({
  getByOwner   : jest.fn().mockResolvedValue([]),
  getAll       : jest.fn().mockResolvedValue([]),
  getByDeviceId: jest.fn().mockResolvedValue(null),
  create       : jest.fn().mockResolvedValue({ id:1, device_id:'smt-01a', owner_id:1, active:true }),
  setActive    : jest.fn().mockResolvedValue({ id:1, device_id:'smt-01a', active:false }),
  delete       : jest.fn().mockResolvedValue(undefined),
  touchLastSeen: jest.fn().mockResolvedValue(undefined),
}));

// ── alertModel — mocked directly so alerts route doesn't touch Prisma/pg ─────
jest.mock('./src/models/alertModel', () => ({
  create           : jest.fn().mockResolvedValue({ id:1, device_id:'DEV-001', status:'unresolved', created_at: new Date().toISOString() }),
  getAll           : jest.fn().mockResolvedValue([]),
  getById          : jest.fn().mockResolvedValue(null),   // null → 404 in route
  getUnresolved    : jest.fn().mockResolvedValue([]),
  countUnresolved  : jest.fn().mockResolvedValue(0),      // number, not object
  resolve          : jest.fn().mockResolvedValue({ id:1, status:'resolved' }),
  recentlyAlerted  : jest.fn().mockResolvedValue(false),
}));

// ── sensorModel — mocked directly so sensors route doesn't touch Prisma/pg ───
jest.mock('./src/models/sensorModel', () => ({
  saveReading     : jest.fn().mockResolvedValue({ id:1, device_id:'smt-m01a', is_alert:false, recorded_at: new Date().toISOString() }),
  getAll          : jest.fn().mockResolvedValue([]),
  getLive         : jest.fn().mockResolvedValue([]),
  getByDevice     : jest.fn().mockResolvedValue([]),
  getBySensorType : jest.fn().mockResolvedValue([]),
}));

// ── MQTT ─────────────────────────────────────────────────────────────────────
jest.mock('mqtt', () => ({
  connect: jest.fn().mockReturnValue({
    on         : jest.fn(),
    subscribe  : jest.fn(),
    publish    : jest.fn(),
    disconnect : jest.fn(),
  }),
}));

// ── Suppress console noise in test output ────────────────────────────────────
global.console.error = jest.fn();
global.console.warn  = jest.fn();

// -- cleanupService -- mocked so tests never start real intervals
jest.mock('./src/services/cleanupService', () => ({
  pruneOldReadings    : jest.fn().mockResolvedValue(0),
  startCleanupSchedule: jest.fn(),
  stopCleanupSchedule : jest.fn(),
  TTL_MINUTES: 9,
}));
