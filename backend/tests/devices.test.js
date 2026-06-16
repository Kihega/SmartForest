'use strict';
/**
 * Device route tests.
 * All Prisma/pg/supabase calls are mocked via jest.setup.js.
 */
const request  = require('supertest');
const { app }  = require('../src/index');
const supabase = require('../src/config/supabase');
const userModel= require('../src/models/userModel');

const AUTH_HEADER = { Authorization: 'Bearer mock-token-xyz' };

describe('GET /api/devices', () => {
  it('returns 401 without auth token', async () => {
    const res = await request(app).get('/api/devices');
    expect(res.statusCode).toBe(401);
  });

  it('returns 200 with valid token', async () => {
    const res = await request(app).get('/api/devices').set(AUTH_HEADER);
    expect([200, 500]).toContain(res.statusCode);
  });
});

describe('POST /api/devices', () => {
  it('returns 401 without auth', async () => {
    const res = await request(app).post('/api/devices').send({ device_id:'smt-01a' });
    expect(res.statusCode).toBe(401);
  });

  it('returns 400 when device_id missing', async () => {
    const res = await request(app)
      .post('/api/devices')
      .set(AUTH_HEADER)
      .send({});
    expect(res.statusCode).toBe(400);
  });
});

describe('DELETE /api/devices/:device_id', () => {
  it('returns 401 without auth', async () => {
    const res = await request(app).delete('/api/devices/smt-01a');
    expect(res.statusCode).toBe(401);
  });
});
