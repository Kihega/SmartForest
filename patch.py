#!/usr/bin/env python3
"""
SmartForest — Fix Jest CI Test Failures
=========================================
Run:  python fix_jest_tests.py /path/to/SmartForest-main

Root cause of CI failure:
  1. deviceModel, alertModel, sensorModel were NOT mocked in jest.setup.js
     → tests that triggered routes importing these models would fail/error
  2. Tests had loose expectations that could misfire (e.g. expect([200,500]))
  3. Missing test cases for 201, 403, 409 responses

This patch rewrites:
  backend/jest.setup.js          — adds deviceModel, alertModel, sensorModel mocks
  backend/tests/auth.test.js     — precise expectations, full route coverage
  backend/tests/alerts.test.js   — model mock overrides, all routes covered
  backend/tests/sensors.test.js  — model mock overrides, all routes covered
  backend/tests/devices.test.js  — full CRUD coverage with ownership checks
  backend/tests/admin.test.js    — all edge cases including last-admin guard
"""
import os, sys

def resolve_root():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    candidate = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(candidate, 'backend', 'package.json')):
        return candidate
    sys.exit('Usage: python fix_jest_tests.py /path/to/SmartForest-main')

ROOT = resolve_root()

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK  {rel}')


FILES = {
    'backend/jest.setup.js': ''''use strict';
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
''',
    'backend/tests/auth.test.js': ''''use strict';
const request = require('supertest');
const { app } = require('../src/index');

describe('POST /api/auth/login', () => {
  it('returns 400 when body is empty', async () => {
    const res = await request(app).post('/api/auth/login').send({});
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when email is missing', async () => {
    const res = await request(app).post('/api/auth/login').send({ password: 'test1234' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when password is missing', async () => {
    const res = await request(app).post('/api/auth/login').send({ email: 'a@b.com' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 200 with token and user on valid credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'password123' });
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('token');
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toHaveProperty('email', 'test@example.com');
  });
});

describe('POST /api/auth/register', () => {
  it('returns 400 when firstName is missing', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'a@b.com', password: 'pass1234' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when password is too short', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Jo', email: 'jo@b.com', password: '123' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 201 on valid registration', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Alice', surName: 'Smith',
              email: 'alice@example.com', password: 'SecurePass1!' });
    expect(res.statusCode).toBe(201);
  });
});

describe('POST /api/auth/logout', () => {
  it('returns 200', async () => {
    const res = await request(app).post('/api/auth/logout');
    expect(res.statusCode).toBe(200);
  });
});

describe('GET /api/auth/me', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).get('/api/auth/me');
    expect(res.statusCode).toBe(401);
  });

  it('returns 200 with valid token', async () => {
    const res = await request(app)
      .get('/api/auth/me')
      .set('Authorization', 'Bearer mock-token-xyz');
    expect(res.statusCode).toBe(200);
  });
});
''',
    'backend/tests/alerts.test.js': ''''use strict';
const request    = require('supertest');
const { app }    = require('../src/index');
const alertModel = require('../src/models/alertModel');

describe('GET /api/health', () => {
  it('returns status ok', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('status', 'ok');
    expect(res.body).toHaveProperty('timestamp');
  });
});

describe('GET /api/alerts', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/alerts');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns empty array when no alerts (mock default)', async () => {
    const res = await request(app).get('/api/alerts');
    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual([]);
  });

  it('returns alerts when model returns data', async () => {
    alertModel.getAll.mockResolvedValueOnce([
      { id:1, device_id:'MIC-001', alert_type:'illegal_logging',
        status:'unresolved', created_at: new Date().toISOString() },
    ]);
    const res = await request(app).get('/api/alerts');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0]).toHaveProperty('device_id', 'MIC-001');
  });
});

describe('GET /api/alerts/count', () => {
  it('returns 200 with a count property', async () => {
    const res = await request(app).get('/api/alerts/count');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('count');
  });

  it('count is a number', async () => {
    const res = await request(app).get('/api/alerts/count');
    expect(typeof res.body.count).toBe('number');
  });

  it('returns correct count from model', async () => {
    alertModel.countUnresolved.mockResolvedValueOnce(5);
    const res = await request(app).get('/api/alerts/count');
    expect(res.body.count).toBe(5);
  });
});

describe('GET /api/alerts/:id', () => {
  it('returns 404 when alert not found (model returns null)', async () => {
    // mock default already returns null
    const res = await request(app).get('/api/alerts/999999');
    expect(res.statusCode).toBe(404);
    expect(res.body).toHaveProperty('error');
  });

  it('returns 200 when alert exists', async () => {
    alertModel.getById.mockResolvedValueOnce({
      id: 1, device_id: 'MIC-001', status: 'unresolved',
      created_at: new Date().toISOString(),
    });
    const res = await request(app).get('/api/alerts/1');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('id', 1);
  });
});

describe('PATCH /api/alerts/:id/resolve', () => {
  it('returns 404 for non-existent alert', async () => {
    alertModel.resolve.mockResolvedValueOnce(null);
    const res = await request(app).patch('/api/alerts/999/resolve');
    expect(res.statusCode).toBe(404);
  });

  it('returns 200 when alert resolved', async () => {
    alertModel.resolve.mockResolvedValueOnce({ id:1, status:'resolved' });
    const res = await request(app).patch('/api/alerts/1/resolve');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
  });
});
''',
    'backend/tests/sensors.test.js': ''''use strict';
const request     = require('supertest');
const { app }     = require('../src/index');
const sensorModel = require('../src/models/sensorModel');

describe('GET /api/sensors/live', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors/live');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns live sensor data when model has data', async () => {
    sensorModel.getLive.mockResolvedValueOnce([
      { id:1, device_id:'MIC-001', sensor_type:'microphone',
        zone:'Kibiti-North', sound_db:45.5, is_alert:false,
        recorded_at: new Date().toISOString() },
    ]);
    const res = await request(app).get('/api/sensors/live');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0]).toHaveProperty('device_id', 'MIC-001');
  });
});

describe('GET /api/sensors', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('GET /api/sensors/:device_id', () => {
  it('returns 200 and array for a specific device', async () => {
    sensorModel.getByDevice.mockResolvedValueOnce([
      { id:1, device_id:'MIC-001', sound_db:45.5, is_alert:false },
    ]);
    const res = await request(app).get('/api/sensors/MIC-001');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/sensors', () => {
  it('returns 400 when device_id is missing', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({ sensor_type: 'microphone', sound_db: 45.0 });
    expect(res.statusCode).toBe(400);
    expect(res.body).toHaveProperty('error');
  });

  it('returns 201 for valid microphone reading', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({ device_id: 'smt-m01a', sensor_type: 'microphone',
              zone: 'Kibiti-North', sound_db: 45.0 });
    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('message');
    expect(res.body).toHaveProperty('data');
  });

  it('returns 201 for valid flame reading', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({ device_id: 'smt-f01a', sensor_type: 'flame',
              zone: 'Kibiti-South', flame_detected: false, temperature_c: 28.5 });
    expect(res.statusCode).toBe(201);
  });
});
''',
    'backend/tests/devices.test.js': ''''use strict';
const request     = require('supertest');
const { app }     = require('../src/index');
const deviceModel = require('../src/models/deviceModel');
const userModel   = require('../src/models/userModel');

const AUTH = { Authorization: 'Bearer mock-token-xyz' };

describe('GET /api/devices', () => {
  it('returns 401 without auth token', async () => {
    const res = await request(app).get('/api/devices');
    expect(res.statusCode).toBe(401);
  });

  it('returns 200 with valid token', async () => {
    const res = await request(app).get('/api/devices').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns devices owned by the user', async () => {
    deviceModel.getByOwner.mockResolvedValueOnce([
      { id:1, device_id:'smt-01a', owner_id:1, active:true },
    ]);
    const res = await request(app).get('/api/devices').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0]).toHaveProperty('device_id', 'smt-01a');
  });
});

describe('GET /api/devices/all', () => {
  it('returns 403 for non-admin user', async () => {
    // default mock returns role:'ranger'
    const res = await request(app).get('/api/devices/all').set(AUTH);
    expect(res.statusCode).toBe(403);
  });

  it('returns 200 for admin user', async () => {
    userModel.getByEmail.mockResolvedValueOnce({ id:1, email:'admin@smartforest.tz', role:'admin' });
    deviceModel.getAll.mockResolvedValueOnce([
      { id:1, device_id:'smt-01a', owner_email:'user@test.com', active:true },
    ]);
    const res = await request(app).get('/api/devices/all').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/devices', () => {
  it('returns 401 without auth', async () => {
    const res = await request(app).post('/api/devices').send({ device_id: 'smt-01a' });
    expect(res.statusCode).toBe(401);
  });

  it('returns 400 when device_id missing', async () => {
    const res = await request(app).post('/api/devices').set(AUTH).send({});
    expect(res.statusCode).toBe(400);
    expect(res.body).toHaveProperty('error');
  });

  it('returns 201 when device registered successfully', async () => {
    // getByDeviceId returns null (device not yet registered)
    deviceModel.getByDeviceId.mockResolvedValueOnce(null);
    deviceModel.create.mockResolvedValueOnce({ id:1, device_id:'smt-new', owner_id:1, active:true });
    const res = await request(app)
      .post('/api/devices').set(AUTH).send({ device_id: 'smt-new' });
    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('device_id', 'smt-new');
  });

  it('returns 409 when device already registered', async () => {
    deviceModel.getByDeviceId.mockResolvedValueOnce({ id:1, device_id:'smt-01a' });
    const res = await request(app)
      .post('/api/devices').set(AUTH).send({ device_id: 'smt-01a' });
    expect(res.statusCode).toBe(409);
  });
});

describe('PATCH /api/devices/:device_id/status', () => {
  it('returns 401 without auth', async () => {
    const res = await request(app).patch('/api/devices/smt-01a/status').send({ active: false });
    expect(res.statusCode).toBe(401);
  });

  it('returns 200 when status updated', async () => {
    deviceModel.setActive.mockResolvedValueOnce({ id:1, device_id:'smt-01a', active:false });
    const res = await request(app)
      .patch('/api/devices/smt-01a/status')
      .set(AUTH)
      .send({ active: false });
    expect(res.statusCode).toBe(200);
  });

  it('returns 404 when device not found', async () => {
    deviceModel.setActive.mockResolvedValueOnce(null);
    const res = await request(app)
      .patch('/api/devices/ghost-99/status')
      .set(AUTH)
      .send({ active: false });
    expect(res.statusCode).toBe(404);
  });
});

describe('DELETE /api/devices/:device_id', () => {
  it('returns 401 without auth', async () => {
    const res = await request(app).delete('/api/devices/smt-01a');
    expect(res.statusCode).toBe(401);
  });

  it('returns 404 when device not found', async () => {
    deviceModel.getByDeviceId.mockResolvedValueOnce(null);
    const res = await request(app).delete('/api/devices/ghost-99').set(AUTH);
    expect(res.statusCode).toBe(404);
  });

  it('returns 200 when device deleted', async () => {
    deviceModel.getByDeviceId.mockResolvedValueOnce({ id:1, device_id:'smt-01a', owner_id:1 });
    const res = await request(app).delete('/api/devices/smt-01a').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
  });

  it('returns 403 when user does not own device', async () => {
    // device owned by owner_id:99, but auth user has id:1
    deviceModel.getByDeviceId.mockResolvedValueOnce({ id:2, device_id:'smt-99', owner_id:99 });
    const res = await request(app).delete('/api/devices/smt-99').set(AUTH);
    expect(res.statusCode).toBe(403);
  });
});
''',
    'backend/tests/admin.test.js': ''''use strict';
const request   = require('supertest');
const { app }   = require('../src/index');
const userModel = require('../src/models/userModel');

const AUTH = { Authorization: 'Bearer mock-token-xyz' };

// Helper: make the requesting user an admin for one call
function asAdmin() {
  userModel.getByEmail.mockResolvedValueOnce({
    id:1, email:'admin@smartforest.tz', role:'admin', name:'Admin',
  });
}

describe('GET /api/admin/users', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).get('/api/admin/users');
    expect(res.statusCode).toBe(401);
  });

  it('returns 403 for non-admin (default mock is ranger)', async () => {
    const res = await request(app).get('/api/admin/users').set(AUTH);
    expect(res.statusCode).toBe(403);
  });

  it('returns 200 for admin and array of users', async () => {
    asAdmin();
    userModel.getAll.mockResolvedValueOnce([
      { id:1, email:'admin@smartforest.tz', role:'admin' },
      { id:2, email:'user@smartforest.tz',  role:'ranger' },
    ]);
    const res = await request(app).get('/api/admin/users').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body).toHaveLength(2);
  });
});

describe('DELETE /api/admin/users/:id', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).delete('/api/admin/users/2');
    expect(res.statusCode).toBe(401);
  });

  it('returns 403 for non-admin', async () => {
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(403);
  });

  it('returns 404 when target user not found', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce(null);
    const res = await request(app).delete('/api/admin/users/999').set(AUTH);
    expect(res.statusCode).toBe(404);
  });

  it('blocks deletion of last admin — returns 400', async () => {
    asAdmin();
    // Target is also an admin
    userModel.getById.mockResolvedValueOnce({ id:2, role:'admin', email:'other@smartforest.tz' });
    // Only 1 admin in the system
    userModel.getAll.mockResolvedValueOnce([
      { id:2, role:'admin' },
    ]);
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/last admin/i);
  });

  it('allows deletion when 2+ admins exist', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce({ id:2, role:'admin', email:'other@smartforest.tz' });
    // 2 admins exist — deletion allowed
    userModel.getAll.mockResolvedValueOnce([
      { id:1, role:'admin' },
      { id:2, role:'admin' },
    ]);
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
  });

  it('allows deletion of non-admin user', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce({ id:3, role:'ranger', email:'ranger@smartforest.tz' });
    const res = await request(app).delete('/api/admin/users/3').set(AUTH);
    expect(res.statusCode).toBe(200);
  });
});
''',
}


for rel, content in FILES.items():
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK  {rel}')

print()
print('Done! Now run:  cd backend && npm test')
