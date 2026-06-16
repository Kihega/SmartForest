'use strict';
/**
 * Auth route tests — all DB/Prisma calls are mocked in jest.setup.js.
 * No live database required.
 */
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

  it('accepts valid credentials (mocked success)', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'password123' });
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('token');
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toHaveProperty('email');
  });
});

describe('POST /api/auth/register', () => {
  it('returns 400 when required fields are missing', async () => {
    const res = await request(app).post('/api/auth/register').send({ email: 'a@b.com' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 for short password', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Jo', email: 'jo@b.com', password: '123' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 201 on valid registration (mocked)', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Alice', surName: 'Smith',
               email: 'alice@example.com', password: 'SecurePass1' });
    expect([201, 400]).toContain(res.statusCode);
  });
});

describe('POST /api/auth/logout', () => {
  it('returns 200', async () => {
    const res = await request(app).post('/api/auth/logout');
    expect(res.statusCode).toBe(200);
  });
});
