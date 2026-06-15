jest.mock('../src/config/db', () => ({
  query: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 })
}));

const request = require('supertest');
const { app } = require('../src/index');

describe('GET /api/sensors/live', () => {
  it('returns 200 and an array', async () => {
    const res = await request(app).get('/api/sensors/live');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});
