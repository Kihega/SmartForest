'use strict';
const express     = require('express');
const router      = express.Router();
const deviceModel = require('../models/deviceModel');
const userModel   = require('../models/userModel');
const supabase    = require('../config/supabase');

/* ── Auth helper ─────────────────────────────────────────────────────────── */
async function getUser(req) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return null;
  const { data, error } = await supabase.auth.getUser(token);
  if (error || !data.user) return null;
  return userModel.getByEmail(data.user.email);
}

// GET /api/devices — current user's devices
router.get('/', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });
    res.json(await deviceModel.getByOwner(user.id));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/devices/all — admin: every device
router.get('/all', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user || user.role !== 'admin')
      return res.status(403).json({ error: 'Admin only' });
    res.json(await deviceModel.getAll());
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/devices — register a device to current user
router.post('/', async (req, res) => {
  const { device_id } = req.body;
  if (!device_id) return res.status(400).json({ error: 'device_id is required' });
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const existing = await deviceModel.getByDeviceId(device_id);
    if (existing) return res.status(409).json({ error: 'Device already registered' });

    const device = await deviceModel.create({ device_id, owner_id: user.id });
    res.status(201).json(device);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/devices/:device_id/status — suspend / resume
router.patch('/:device_id/status', async (req, res) => {
  const { device_id } = req.params;
  const { active }    = req.body;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const ownerFilter = user.role === 'admin' ? null : user.id;
    const result = await deviceModel.setActive(device_id, active, ownerFilter);
    if (!result) return res.status(404).json({ error: 'Device not found or not yours' });
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/devices/:device_id — unregister + cascade
router.delete('/:device_id', async (req, res) => {
  const { device_id } = req.params;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const existing = await deviceModel.getByDeviceId(device_id);
    if (!existing) return res.status(404).json({ error: 'Device not found' });
    if (user.role !== 'admin' && existing.owner_id !== user.id)
      return res.status(403).json({ error: 'Not your device' });

    await deviceModel.delete(device_id);
    res.json({ message: `Device ${device_id} deleted` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
