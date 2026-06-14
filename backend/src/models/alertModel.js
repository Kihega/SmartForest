const pool = require('../config/db');

const alertModel = {

  // Insert a new alert
  async create(data) {
    const { device_id, zone, latitude,
            longitude, sound_db, vibration } = data;
    const result = await pool.query(
      `INSERT INTO alerts
         (device_id, zone, latitude, longitude, sound_db, vibration)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [device_id, zone, latitude, longitude, sound_db, vibration]
    );
    return result.rows[0];
  },

  // Get all alerts ordered by newest first
  async getAll(limit = 100) {
    const result = await pool.query(
      `SELECT * FROM alerts
       ORDER BY created_at DESC LIMIT $1`,
      [limit]
    );
    return result.rows;
  },

  // Get single alert by id
  async getById(id) {
    const result = await pool.query(
      'SELECT * FROM alerts WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  },

  // Get all unresolved alerts
  async getUnresolved() {
    const result = await pool.query(
      `SELECT * FROM alerts
       WHERE  status = 'unresolved'
       ORDER  BY created_at DESC`
    );
    return result.rows;
  },

  // Count unresolved alerts (for navbar badge)
  async countUnresolved() {
    const result = await pool.query(
      `SELECT COUNT(*) FROM alerts WHERE status = 'unresolved'`
    );
    return parseInt(result.rows[0].count, 10);
  },

  // Mark alert as resolved
  async resolve(id) {
    const result = await pool.query(
      `UPDATE alerts SET status = 'resolved'
       WHERE id = $1 RETURNING *`,
      [id]
    );
    return result.rows[0] || null;
  },

  // Check if same device alerted recently (deduplication)
  // Returns true if an alert exists for this device in last N minutes
  async recentlyAlerted(device_id, minutes = 5) {
    const result = await pool.query(
      `SELECT id FROM alerts
       WHERE  device_id = $1
       AND    created_at > NOW() - INTERVAL '$2 minutes'
       LIMIT  1`,
      [device_id, minutes]
    );
    return result.rows.length > 0;
  },

};

module.exports = alertModel;
