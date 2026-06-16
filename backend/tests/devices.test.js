'use strict';
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
