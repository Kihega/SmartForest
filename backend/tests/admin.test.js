'use strict';
const request   = require('supertest');
const { app }   = require('../src/index');
const userModel = require('../src/models/userModel');

const AUTH = { Authorization: 'Bearer mock-token-xyz' };

// Helper: make the requesting user an admin for one call
function asAdmin() {
  userModel.getByEmail.mockResolvedValueOnce({
    id:1, email:'admin@smartforest.tz', role:'admin', name:'Admin',
  });
}

describe('GET /api/admin/users', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).get('/api/admin/users');
    expect(res.statusCode).toBe(401);
  });

  it('returns 403 for non-admin (default mock is ranger)', async () => {
    const res = await request(app).get('/api/admin/users').set(AUTH);
    expect(res.statusCode).toBe(403);
  });

  it('returns 200 for admin and array of users', async () => {
    asAdmin();
    userModel.getAll.mockResolvedValueOnce([
      { id:1, email:'admin@smartforest.tz', role:'admin' },
      { id:2, email:'user@smartforest.tz',  role:'ranger' },
    ]);
    const res = await request(app).get('/api/admin/users').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body).toHaveLength(2);
  });
});

describe('DELETE /api/admin/users/:id', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).delete('/api/admin/users/2');
    expect(res.statusCode).toBe(401);
  });

  it('returns 403 for non-admin', async () => {
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(403);
  });

  it('returns 404 when target user not found', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce(null);
    const res = await request(app).delete('/api/admin/users/999').set(AUTH);
    expect(res.statusCode).toBe(404);
  });

  it('blocks deletion of last admin — returns 400', async () => {
    asAdmin();
    // Target is also an admin
    userModel.getById.mockResolvedValueOnce({ id:2, role:'admin', email:'other@smartforest.tz' });
    // Only 1 admin in the system
    userModel.getAll.mockResolvedValueOnce([
      { id:2, role:'admin' },
    ]);
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/last admin/i);
  });

  it('allows deletion when 2+ admins exist', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce({ id:2, role:'admin', email:'other@smartforest.tz' });
    // 2 admins exist — deletion allowed
    userModel.getAll.mockResolvedValueOnce([
      { id:1, role:'admin' },
      { id:2, role:'admin' },
    ]);
    const res = await request(app).delete('/api/admin/users/2').set(AUTH);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
  });

  it('allows deletion of non-admin user', async () => {
    asAdmin();
    userModel.getById.mockResolvedValueOnce({ id:3, role:'ranger', email:'ranger@smartforest.tz' });
    const res = await request(app).delete('/api/admin/users/3').set(AUTH);
    expect(res.statusCode).toBe(200);
  });
});
