'use strict';
const request  = require('supertest');
const { app }  = require('../src/index');
const userModel= require('../src/models/userModel');

const ADMIN_HEADER  = { Authorization: 'Bearer mock-admin-token' };
const RANGER_HEADER = { Authorization: 'Bearer mock-ranger-token' };

describe('GET /api/admin/users', () => {
  it('returns 401 without token', async () => {
    const res = await request(app).get('/api/admin/users');
    expect(res.statusCode).toBe(401);
  });

  it('returns 403 for non-admin user', async () => {
    // userModel.getByEmail mock returns role:'ranger' by default
    const res = await request(app).get('/api/admin/users').set(RANGER_HEADER);
    expect(res.statusCode).toBe(403);
  });

  it('returns 200 for admin user', async () => {
    // Override mock: make this user an admin
    userModel.getByEmail.mockResolvedValueOnce({
      id:1, email:'admin@smartforest.tz', role:'admin', name:'Admin',
    });
    const res = await request(app).get('/api/admin/users').set(ADMIN_HEADER);
    expect(res.statusCode).toBe(200);
  });
});

describe('DELETE /api/admin/users/:id', () => {
  it('blocks deletion of last admin', async () => {
    // Admin requesting, target is also admin, only 1 admin total
    userModel.getByEmail.mockResolvedValueOnce({ id:1, role:'admin', email:'a@b.com' });
    userModel.getById.mockResolvedValueOnce({ id:2, role:'admin', email:'b@b.com' });
    userModel.getAll.mockResolvedValueOnce([
      { id:1, role:'admin' }, // only 1 admin
    ]);
    const res = await request(app)
      .delete('/api/admin/users/2')
      .set(ADMIN_HEADER);
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/last admin/i);
  });
});
