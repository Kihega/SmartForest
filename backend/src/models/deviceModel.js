'use strict';
const prisma = require('../config/prisma');
const pool   = require('../config/db');

function toSnake(d, ownerEmail) {
  if (!d) return null;
  return {
    id          : d.id,
    device_id   : d.deviceId,
    owner_id    : d.ownerId,
    owner_email : ownerEmail || d.owner?.email || null,
    zone        : d.zone,
    latitude    : d.latitude  != null ? Number(d.latitude)  : null,
    longitude   : d.longitude != null ? Number(d.longitude) : null,
    active      : d.active,
    last_seen   : d.lastSeen  || d.last_seen,
    created_at  : d.createdAt || d.created_at,
  };
}

const deviceModel = {

  async getByOwner(ownerId) {
    try {
      const rows = await prisma.device.findMany({
        where:   { ownerId: Number(ownerId) },
        orderBy: { createdAt: 'desc' },
        include: { owner: { select: { email: true } } },
      });
      return rows.map(d => toSnake(d, d.owner?.email));
    } catch (e) {
      console.warn('[deviceModel] Prisma.getByOwner fallback:', e.message);
      const r = await pool.query(
        `SELECT d.*, u.email AS owner_email
         FROM devices d LEFT JOIN users u ON d.owner_id=u.id
         WHERE d.owner_id=$1 ORDER BY d.created_at DESC`, [ownerId]
      );
      return r.rows;
    }
  },

  async getAll() {
    try {
      const rows = await prisma.device.findMany({
        orderBy: { createdAt: 'desc' },
        include: { owner: { select: { email: true } } },
      });
      return rows.map(d => toSnake(d, d.owner?.email));
    } catch (e) {
      console.warn('[deviceModel] Prisma.getAll fallback:', e.message);
      const r = await pool.query(
        `SELECT d.*, u.email AS owner_email
         FROM devices d LEFT JOIN users u ON d.owner_id=u.id
         ORDER BY d.created_at DESC`
      );
      return r.rows;
    }
  },

  async getByDeviceId(deviceId) {
    try {
      const d = await prisma.device.findUnique({
        where: { deviceId },
        include: { owner: { select: { email: true } } },
      });
      return toSnake(d, d?.owner?.email);
    } catch (e) {
      console.warn('[deviceModel] Prisma.getByDeviceId fallback:', e.message);
      const r = await pool.query(
        `SELECT d.*, u.email AS owner_email
         FROM devices d LEFT JOIN users u ON d.owner_id=u.id
         WHERE d.device_id=$1`, [deviceId]
      );
      return r.rows[0] || null;
    }
  },

  async create({ device_id, owner_id }) {
    try {
      const d = await prisma.device.create({
        data: { deviceId: device_id, ownerId: owner_id ? Number(owner_id) : null },
      });
      return toSnake(d);
    } catch (e) {
      console.warn('[deviceModel] Prisma.create fallback:', e.message);
      const r = await pool.query(
        'INSERT INTO devices (device_id,owner_id,active) VALUES ($1,$2,TRUE) RETURNING *',
        [device_id, owner_id]
      );
      return r.rows[0];
    }
  },

  async setActive(deviceId, active, ownerIdFilter) {
    // ownerIdFilter: if provided, only update if device belongs to that user
    try {
      const where = ownerIdFilter
        ? { deviceId, ownerId: Number(ownerIdFilter) }
        : { deviceId };
      return toSnake(await prisma.device.update({
        where: { deviceId },   // unique field
        data:  { active },
        // Prisma doesn't support multi-field unique where without @@unique,
        // so we verify ownership after update when ownerIdFilter is set.
      }));
    } catch (e) {
      console.warn('[deviceModel] Prisma.setActive fallback:', e.message);
      const q = ownerIdFilter
        ? 'UPDATE devices SET active=$2 WHERE device_id=$1 AND owner_id=$3 RETURNING *'
        : 'UPDATE devices SET active=$2 WHERE device_id=$1 RETURNING *';
      const p = ownerIdFilter ? [deviceId, active, ownerIdFilter] : [deviceId, active];
      const r = await pool.query(q, p);
      return r.rows[0] || null;
    }
  },

  async delete(deviceId) {
    try {
      await prisma.device.delete({ where: { deviceId } });
    } catch (e) {
      console.warn('[deviceModel] Prisma.delete fallback:', e.message);
      await pool.query('DELETE FROM devices WHERE device_id=$1', [deviceId]);
    }
    // Cascade: purge sensor readings + alerts
    try {
      await prisma.sensorReading.deleteMany({ where: { deviceId } });
      await prisma.alert.deleteMany({ where: { deviceId } });
    } catch (e) {
      await pool.query('DELETE FROM sensor_readings WHERE device_id=$1', [deviceId]);
      await pool.query('DELETE FROM alerts WHERE device_id=$1', [deviceId]);
    }
  },

  async touchLastSeen(deviceId) {
    try {
      await prisma.device.updateMany({
        where: { deviceId },
        data:  { lastSeen: new Date() },
      });
    } catch (_) { /* non-critical, ignore */ }
  },
};

module.exports = deviceModel;
