'use strict';
const prisma = require('../config/prisma');
const pool   = require('../config/db');

function toSnake(a) {
  if (!a) return null;
  return {
    id             : a.id,
    device_id      : a.deviceId,
    sensor_type    : a.sensorType,
    alert_type     : a.alertType,
    zone           : a.zone,
    latitude       : a.latitude != null ? Number(a.latitude)    : null,
    longitude      : a.longitude != null ? Number(a.longitude)  : null,
    sound_db       : a.soundDb != null ? Number(a.soundDb)      : null,
    flame_detected : a.flameDetected,
    temperature_c  : a.temperatureC != null ? Number(a.temperatureC) : null,
    status         : a.status,
    resolved_by    : a.resolvedById,
    created_at     : a.createdAt || a.created_at,
  };
}

const alertModel = {

  async create(data) {
    const {
      device_id, sensor_type = 'microphone',
      alert_type = 'illegal_logging',
      zone, latitude, longitude,
      sound_db, flame_detected, temperature_c,
    } = data;
    try {
      const a = await prisma.alert.create({
        data: {
          deviceId      : device_id,
          sensorType    : sensor_type,
          alertType     : alert_type,
          zone, latitude, longitude,
          soundDb       : sound_db       ?? null,
          flameDetected : flame_detected ?? false,
          temperatureC  : temperature_c  ?? null,
        },
      });
      return toSnake(a);
    } catch (e) {
      console.warn('[alertModel] Prisma.create fallback:', e.message);
      const r = await pool.query(
        `INSERT INTO alerts
           (device_id,sensor_type,alert_type,zone,latitude,longitude,
            sound_db,flame_detected,temperature_c)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING *`,
        [device_id,sensor_type,alert_type,zone,latitude,longitude,
         sound_db??null, flame_detected??false, temperature_c??null]
      );
      return r.rows[0];
    }
  },

  async getAll(limit = 100) {
    try {
      const rows = await prisma.alert.findMany({
        orderBy: { createdAt: 'desc' },
        take: limit,
      });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[alertModel] Prisma.getAll fallback:', e.message);
      const r = await pool.query(
        'SELECT * FROM alerts ORDER BY created_at DESC LIMIT $1', [limit]
      );
      return r.rows;
    }
  },

  async getById(id) {
    try {
      return toSnake(await prisma.alert.findUnique({ where: { id: Number(id) } }));
    } catch (e) {
      console.warn('[alertModel] Prisma.getById fallback:', e.message);
      const r = await pool.query('SELECT * FROM alerts WHERE id=$1', [id]);
      return r.rows[0] || null;
    }
  },

  async getUnresolved() {
    try {
      const rows = await prisma.alert.findMany({
        where:   { status: 'unresolved' },
        orderBy: { createdAt: 'desc' },
      });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[alertModel] Prisma.getUnresolved fallback:', e.message);
      const r = await pool.query(
        "SELECT * FROM alerts WHERE status='unresolved' ORDER BY created_at DESC"
      );
      return r.rows;
    }
  },

  async countUnresolved() {
    try {
      return await prisma.alert.count({ where: { status: 'unresolved' } });
    } catch (e) {
      console.warn('[alertModel] Prisma.countUnresolved fallback:', e.message);
      const r = await pool.query(
        "SELECT COUNT(*) FROM alerts WHERE status='unresolved'"
      );
      return parseInt(r.rows[0].count, 10);
    }
  },

  async resolve(id) {
    try {
      return toSnake(await prisma.alert.update({
        where: { id: Number(id) },
        data:  { status: 'resolved' },
      }));
    } catch (e) {
      console.warn('[alertModel] Prisma.resolve fallback:', e.message);
      const r = await pool.query(
        "UPDATE alerts SET status='resolved' WHERE id=$1 RETURNING *", [id]
      );
      return r.rows[0] || null;
    }
  },

  async recentlyAlerted(device_id, minutes = 5) {
    try {
      const since = new Date(Date.now() - minutes * 60_000);
      const count = await prisma.alert.count({
        where: { deviceId: device_id, createdAt: { gte: since } },
      });
      return count > 0;
    } catch (e) {
      console.warn('[alertModel] Prisma.recentlyAlerted fallback:', e.message);
      const r = await pool.query(
        `SELECT id FROM alerts
         WHERE device_id=$1 AND created_at > NOW()-($2||' minutes')::INTERVAL
         LIMIT 1`,
        [device_id, minutes]
      );
      return r.rows.length > 0;
    }
  },
};

module.exports = alertModel;
