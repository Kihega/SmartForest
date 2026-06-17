
'use strict';
const prisma = require('../config/prisma');
const pool   = require('../config/db');

const TTL_MINUTES = parseInt(process.env.SENSOR_TTL_MINUTES || '9', 10);

function toSnake(s) {
  if (!s) return null;
  return {
    id             : s.id,
    device_id      : s.deviceId,
    sensor_type    : s.sensorType,
    zone           : s.zone,
    latitude       : s.latitude  != null ? Number(s.latitude)  : null,
    longitude      : s.longitude != null ? Number(s.longitude) : null,
    sound_db       : s.soundDb       != null ? Number(s.soundDb)      : null,
    flame_detected : s.flameDetected,
    temperature_c  : s.temperatureC  != null ? Number(s.temperatureC) : null,
    is_alert       : s.isAlert,
    recorded_at    : s.recordedAt || s.recorded_at,
  };
}

// Opportunistic prune — runs after every write so stale rows never linger
// even if the scheduled cleanupService tick hasn't fired yet.
// Fire-and-forget: never blocks or fails the write that triggered it.
function pruneAsync() {
  const cutoff = new Date(Date.now() - TTL_MINUTES * 60000);
  prisma.sensorReading.deleteMany({ where: { recordedAt: { lt: cutoff } } })
    .catch(() => {
      const sql = "DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '" + TTL_MINUTES + " minutes'";
      pool.query(sql).catch(() => { /* best-effort, ignore */ });
    });
}

const sensorModel = {

  async saveReading(data) {
    const {
      device_id, sensor_type = 'microphone',
      zone, latitude, longitude,
      sound_db, flame_detected, temperature_c, is_alert,
    } = data;
    let saved;
    try {
      const r = await prisma.sensorReading.create({
        data: {
          deviceId      : device_id,
          sensorType    : sensor_type,
          zone, latitude, longitude,
          soundDb       : sound_db       ?? null,
          flameDetected : flame_detected ?? false,
          temperatureC  : temperature_c  ?? null,
          isAlert       : is_alert       ?? false,
        },
      });
      saved = toSnake(r);
    } catch (e) {
      console.warn('[sensorModel] Prisma.saveReading fallback:', e.message);
      const r = await pool.query(
        `INSERT INTO sensor_readings
           (device_id,sensor_type,zone,latitude,longitude,
            sound_db,flame_detected,temperature_c,is_alert)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING *`,
        [device_id, sensor_type, zone, latitude, longitude,
         sound_db??null, flame_detected??false, temperature_c??null, is_alert??false]
      );
      saved = r.rows[0];
    }
    pruneAsync();   // fire-and-forget TTL sweep
    return saved;
  },

  async getAll(limit = 100) {
    try {
      const rows = await prisma.sensorReading.findMany({
        orderBy: { recordedAt: 'desc' },
        take: limit,
      });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[sensorModel] Prisma.getAll fallback:', e.message);
      const r = await pool.query(
        'SELECT * FROM sensor_readings ORDER BY recorded_at DESC LIMIT $1', [limit]
      );
      return r.rows;
    }
  },

  async getLive() {
    try {
      const devices = await prisma.sensorReading.findMany({
        distinct: ['deviceId'],
        orderBy:  { recordedAt: 'desc' },
        select:   { deviceId: true },
      });
      const rows = await Promise.all(
        devices.map(d =>
          prisma.sensorReading.findFirst({
            where:   { deviceId: d.deviceId },
            orderBy: { recordedAt: 'desc' },
          })
        )
      );
      return rows.filter(Boolean).map(toSnake);
    } catch (e) {
      console.warn('[sensorModel] Prisma.getLive fallback:', e.message);
      const r = await pool.query(
        `SELECT DISTINCT ON (device_id)
                id,device_id,sensor_type,zone,latitude,longitude,
                sound_db,flame_detected,temperature_c,is_alert,recorded_at
         FROM   sensor_readings
         ORDER  BY device_id, recorded_at DESC`
      );
      return r.rows;
    }
  },

  async getByDevice(device_id, limit = 50) {
    try {
      const rows = await prisma.sensorReading.findMany({
        where:   { deviceId: device_id },
        orderBy: { recordedAt: 'desc' },
        take: limit,
      });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[sensorModel] Prisma.getByDevice fallback:', e.message);
      const r = await pool.query(
        'SELECT * FROM sensor_readings WHERE device_id=$1 ORDER BY recorded_at DESC LIMIT $2',
        [device_id, limit]
      );
      return r.rows;
    }
  },

  async getBySensorType(sensor_type, limit = 100) {
    try {
      const rows = await prisma.sensorReading.findMany({
        where:   { sensorType: sensor_type },
        orderBy: { recordedAt: 'desc' },
        take: limit,
      });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[sensorModel] Prisma.getBySensorType fallback:', e.message);
      const r = await pool.query(
        'SELECT * FROM sensor_readings WHERE sensor_type=$1 ORDER BY recorded_at DESC LIMIT $2',
        [sensor_type, limit]
      );
      return r.rows;
    }
  },
};

module.exports = sensorModel;
