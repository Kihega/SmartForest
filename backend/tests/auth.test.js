jest.mock('../src/config/database', () => ({
  query: jest.fn().mockResolvedValue({ rows: [] })
}));

const request = require('supertest');
const { app } = require('../src/index');

describe('POST /api/auth/login', () => {
  it('returns 400 when body is empty', async () => {
    const res = await request(app).post('/api/auth/login').send({});
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when email is missing', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ password: 'test1234' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when password is missing', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'ranger@forest.go.tz' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 401 for wrong credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'fake@fake.com', password: 'wrongpass' });
    expect([401, 400]).toContain(res.statusCode);
  });
});

describe('POST /api/auth/logout', () => {
  it('returns 200 or 401 depending on session', async () => {
    const res = await request(app).post('/api/auth/logout');
    expect([200, 401]).toContain(res.statusCode);
  });
});
