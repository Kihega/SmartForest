const pool = require('../config/db');

const sensorModel = {

  // Save any sensor reading (microphone or flame)
  async saveReading(data) {
    const {
      device_id, sensor_type = 'microphone',
      zone, latitude, longitude,
      sound_db, flame_detected, temperature_c, is_alert
    } = data;

    const result = await pool.query(
      `INSERT INTO sensor_readings
         (device_id, sensor_type, zone, latitude, longitude,
          sound_db, flame_detected, temperature_c, is_alert)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
       RETURNING *`,
      [
        device_id,
        sensor_type,
        zone,
        latitude,
        longitude,
        sound_db       || null,
        flame_detected || false,
        temperature_c  || null,
        is_alert       || false,
      ]
    );
    return result.rows[0];
  },

  // All readings newest first
  async getAll(limit = 100) {
    const result = await pool.query(
      'SELECT * FROM sensor_readings ORDER BY recorded_at DESC LIMIT $1',
      [limit]
    );
    return result.rows;
  },

  // Latest reading per device
  async getLive() {
    const result = await pool.query(
      `SELECT DISTINCT ON (device_id)
              id, device_id, sensor_type, zone,
              latitude, longitude, sound_db,
              flame_detected, temperature_c,
              is_alert, recorded_at
       FROM   sensor_readings
       ORDER  BY device_id, recorded_at DESC`
    );
    return result.rows;
  },

  // Readings for a specific device
  async getByDevice(device_id, limit = 50) {
    const result = await pool.query(
      `SELECT * FROM sensor_readings
       WHERE  device_id = $1
       ORDER  BY recorded_at DESC LIMIT $2`,
      [device_id, limit]
    );
    return result.rows;
  },

  // Readings filtered by sensor type
  async getBySensorType(sensor_type, limit = 100) {
    const result = await pool.query(
      `SELECT * FROM sensor_readings
       WHERE  sensor_type = $1
       ORDER  BY recorded_at DESC LIMIT $2`,
      [sensor_type, limit]
    );
    return result.rows;
  },

};

module.exports = sensorModel;
