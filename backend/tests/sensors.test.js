'use strict';
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
