'use strict';
const request = require('supertest');
const { app } = require('../src/index');

describe('GET /api/health', () => {
  it('returns status ok', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('status', 'ok');
  });
});

describe('GET /api/alerts', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/alerts');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('count endpoint returns a number', async () => {
    const res = await request(app).get('/api/alerts/count');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('count');
    expect(typeof res.body.count).toBe('number');
  });
});

describe('GET /api/alerts/:id', () => {
  it('returns 404 for non-existent alert', async () => {
    const res = await request(app).get('/api/alerts/999999');
    expect(res.statusCode).toBe(404);
  });
});
