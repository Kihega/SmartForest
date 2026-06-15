const pool = require('../config/db');

const alertModel = {

  async create(data) {
    const {
      device_id, sensor_type = 'microphone',
      alert_type = 'illegal_logging',
      zone, latitude, longitude,
      sound_db, flame_detected, temperature_c
    } = data;

    const result = await pool.query(
      `INSERT INTO alerts
         (device_id, sensor_type, alert_type, zone,
          latitude, longitude,
          sound_db, flame_detected, temperature_c)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
       RETURNING *`,
      [
        device_id, sensor_type, alert_type,
        zone, latitude, longitude,
        sound_db       || null,
        flame_detected || false,
        temperature_c  || null,
      ]
    );
    return result.rows[0];
  },

  async getAll(limit = 100) {
    const result = await pool.query(
      'SELECT * FROM alerts ORDER BY created_at DESC LIMIT $1',
      [limit]
    );
    return result.rows;
  },

  async getById(id) {
    const result = await pool.query(
      'SELECT * FROM alerts WHERE id = $1', [id]
    );
    return result.rows[0] || null;
  },

  async getUnresolved() {
    const result = await pool.query(
      `SELECT * FROM alerts
       WHERE status = 'unresolved'
       ORDER BY created_at DESC`
    );
    return result.rows;
  },

  async countUnresolved() {
    const result = await pool.query(
      `SELECT COUNT(*) FROM alerts WHERE status = 'unresolved'`
    );
    return parseInt(result.rows[0].count, 10);
  },

  async resolve(id) {
    const result = await pool.query(
      `UPDATE alerts SET status = 'resolved'
       WHERE id = $1 RETURNING *`,
      [id]
    );
    return result.rows[0] || null;
  },

  // Deduplication: true if same device alerted in last N minutes
  async recentlyAlerted(device_id, minutes = 5) {
    const result = await pool.query(
      `SELECT id FROM alerts
       WHERE  device_id = $1
       AND    created_at > NOW() - ($2 || ' minutes')::INTERVAL
       LIMIT  1`,
      [device_id, minutes]
    );
    return result.rows.length > 0;
  },

};

module.exports = alertModel;
