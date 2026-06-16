'use strict';
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
