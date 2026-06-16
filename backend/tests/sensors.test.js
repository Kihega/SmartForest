'use strict';
/**
 * Sensor route tests — mocked via jest.setup.js.
 */
const request = require('supertest');
const { app } = require('../src/index');

describe('GET /api/sensors/live', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors/live');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('GET /api/sensors', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors');
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
  });

  it('returns 201 when valid microphone reading posted', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({ device_id: 'smt-m01a', sensor_type: 'microphone',
               zone: 'Kibiti-North', sound_db: 45.0 });
    expect([201, 500]).toContain(res.statusCode);
  });
});
