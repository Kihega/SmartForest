const pool = require('../config/db');

const sensorModel = {

  // Insert a new sensor reading
  async saveReading(data) {
    const { device_id, zone, latitude, longitude,
            sound_db, vibration, is_alert } = data;
    const result = await pool.query(
      `INSERT INTO sensor_readings
         (device_id, zone, latitude, longitude, sound_db, vibration, is_alert)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [device_id, zone, latitude, longitude,
       sound_db, vibration, is_alert || false]
    );
    return result.rows[0];
  },

  // Get all sensor readings ordered by newest first
  async getAll(limit = 100) {
    const result = await pool.query(
      'SELECT * FROM sensor_readings ORDER BY recorded_at DESC LIMIT $1',
      [limit]
    );
    return result.rows;
  },

  // Get the latest reading per device_id
  async getLive() {
    const result = await pool.query(
      `SELECT DISTINCT ON (device_id)
              id, device_id, zone, latitude, longitude,
              sound_db, vibration, is_alert, recorded_at
       FROM   sensor_readings
       ORDER  BY device_id, recorded_at DESC`
    );
    return result.rows;
  },

  // Get readings for a specific device
  async getByDevice(device_id, limit = 50) {
    const result = await pool.query(
      `SELECT * FROM sensor_readings
       WHERE  device_id = $1
       ORDER  BY recorded_at DESC LIMIT $2`,
      [device_id, limit]
    );
    return result.rows;
  },

};

module.exports = sensorModel;
