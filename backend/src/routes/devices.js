const express = require('express');
const router  = express.Router();
const pool    = require('../config/db');
const supabase = require('../config/supabase');

/* helper — get user from bearer token */
async function getUser(req) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return null;
  const { data, error } = await supabase.auth.getUser(token);
  if (error || !data.user) return null;
  const r = await pool.query('SELECT * FROM users WHERE email=$1', [data.user.email]);
  return r.rows[0] || null;
}

// GET /api/devices — list devices owned by current user
router.get('/', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });
    const result = await pool.query(
      `SELECT d.*, u.email AS owner_email
       FROM devices d
       LEFT JOIN users u ON d.owner_id = u.id
       WHERE d.owner_id = $1
       ORDER BY d.created_at DESC`,
      [user.id]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/devices/all — admin: all devices
router.get('/all', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user || user.role !== 'admin')
      return res.status(403).json({ error: 'Admin only' });
    const result = await pool.query(
      `SELECT d.*, u.email AS owner_email
       FROM devices d
       LEFT JOIN users u ON d.owner_id = u.id
       ORDER BY d.created_at DESC`
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/devices — register a new device
router.post('/', async (req, res) => {
  const { device_id } = req.body;
  if (!device_id) return res.status(400).json({ error: 'device_id is required' });
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    // Check if device already claimed
    const existing = await pool.query(
      'SELECT * FROM devices WHERE device_id=$1', [device_id]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ error: 'Device already registered' });
    }

    const result = await pool.query(
      `INSERT INTO devices (device_id, owner_id, active)
       VALUES ($1, $2, TRUE)
       RETURNING *`,
      [device_id, user.id]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/devices/:device_id/status — suspend or resume
router.patch('/:device_id/status', async (req, res) => {
  const { device_id } = req.params;
  const { active }    = req.body;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const filter = user.role === 'admin'
      ? 'WHERE device_id=$1'
      : 'WHERE device_id=$1 AND owner_id=$2';
    const params = user.role === 'admin'
      ? [device_id, active]
      : [device_id, user.id, active];

    // Build update
    const q = user.role === 'admin'
      ? 'UPDATE devices SET active=$2 WHERE device_id=$1 RETURNING *'
      : 'UPDATE devices SET active=$3 WHERE device_id=$1 AND owner_id=$2 RETURNING *';
    const p = user.role === 'admin'
      ? [device_id, active]
      : [device_id, user.id, active];

    const result = await pool.query(q, p);
    if (result.rows.length === 0)
      return res.status(404).json({ error: 'Device not found or not yours' });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/devices/:device_id — unregister device (removes all related data)
router.delete('/:device_id', async (req, res) => {
  const { device_id } = req.params;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const q = user.role === 'admin'
      ? 'DELETE FROM devices WHERE device_id=$1 RETURNING id'
      : 'DELETE FROM devices WHERE device_id=$1 AND owner_id=$2 RETURNING id';
    const p = user.role === 'admin' ? [device_id] : [device_id, user.id];

    const result = await pool.query(q, p);
    if (result.rows.length === 0)
      return res.status(404).json({ error: 'Device not found or not yours' });

    // Cascade: remove sensor readings & alerts for this device
    await pool.query('DELETE FROM sensor_readings WHERE device_id=$1', [device_id]);
    await pool.query('DELETE FROM alerts WHERE device_id=$1', [device_id]);

    res.json({ message: `Device ${device_id} deleted` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
