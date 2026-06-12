const request = require('supertest');
const { app } = require('../src/index');

describe('GET /api/sensors', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('each reading has required fields when data exists', async () => {
    const res = await request(app).get('/api/sensors');
    if (res.body.length > 0) {
      const r = res.body[0];
      expect(r).toHaveProperty('device_id');
      expect(r).toHaveProperty('sound_db');
      expect(r).toHaveProperty('vibration');
      expect(r).toHaveProperty('zone');
    } else {
      expect(res.body).toEqual([]);
    }
  });
});

describe('GET /api/sensors/live', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors/live');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/sensors', () => {
  it('rejects missing device_id with 400', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({ sound_db: 55, vibration: 2 });
    expect(res.statusCode).toBe(400);
  });

  it('accepts valid sensor payload', async () => {
    const res = await request(app)
      .post('/api/sensors')
      .send({
        device_id : 'SENSOR-TEST',
        zone      : 'Kibiti-North',
        latitude  : -7.72,
        longitude : 38.95,
        sound_db  : 45.0,
        vibration : 2.1,
      });
    expect([200, 201]).toContain(res.statusCode);
  });
});
