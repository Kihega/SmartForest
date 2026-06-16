'use strict';
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

  it('returns 200 with token and user on valid credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'password123' });
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('token');
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toHaveProperty('email', 'test@example.com');
  });
});

describe('POST /api/auth/register', () => {
  it('returns 400 when firstName is missing', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ email: 'a@b.com', password: 'pass1234' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 400 when password is too short', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Jo', email: 'jo@b.com', password: '123' });
    expect(res.statusCode).toBe(400);
  });

  it('returns 201 on valid registration', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({ firstName: 'Alice', surName: 'Smith',
              email: 'alice@example.com', password: 'SecurePass1!' });
    expect(res.statusCode).toBe(201);
  });
});

describe('POST /api/auth/logout', () => {
  it('returns 200', async () => {
    const res = await request(app).post('/api/auth/logout');
    expect(res.statusCode).toBe(200);
  });
});

describe('GET /api/auth/me', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).get('/api/auth/me');
    expect(res.statusCode).toBe(401);
  });

  it('returns 200 with valid token', async () => {
    const res = await request(app)
      .get('/api/auth/me')
      .set('Authorization', 'Bearer mock-token-xyz');
    expect(res.statusCode).toBe(200);
  });
});
