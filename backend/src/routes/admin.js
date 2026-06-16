'use strict';
const express   = require('express');
const router    = express.Router();
const userModel = require('../models/userModel');
const supabase  = require('../config/supabase');

async function requireAdmin(req, res) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) { res.status(401).json({ error: 'Not authenticated' }); return null; }
  const { data, error } = await supabase.auth.getUser(token);
  if (error) { res.status(401).json({ error: 'Invalid token' }); return null; }
  const user = await userModel.getByEmail(data.user.email);
  if (!user || user.role !== 'admin') {
    res.status(403).json({ error: 'Admin access required' });
    return null;
  }
  return user;
}

// GET /api/admin/users
router.get('/users', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;
    res.json(await userModel.getAll());
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/admin/users — create admin via Supabase + sync DB
router.post('/users', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;
    const { name, email, password, role } = req.body;
    if (!email || !password)
      return res.status(400).json({ error: 'email and password are required' });

    const { data, error } = await supabase.auth.admin.createUser({
      email, password,
      email_confirm: true,
      user_metadata: { name: name || email, role: role || 'admin' },
    });
    if (error) return res.status(400).json({ error: error.message });

    const profile = await userModel.create({ name: name || email, email, role: role || 'admin' });
    res.status(201).json(profile);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/admin/users/:id — never zero admins
router.delete('/users/:id', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;

    const target = await userModel.getById(req.params.id);
    if (!target) return res.status(404).json({ error: 'User not found' });

    if (target.role === 'admin') {
      const all = await userModel.getAll();
      const adminCount = all.filter(u => u.role === 'admin').length;
      if (adminCount <= 1)
        return res.status(400).json({ error: 'Cannot delete the last admin account' });
    }

    await userModel.delete(req.params.id);
    res.json({ message: 'User deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
