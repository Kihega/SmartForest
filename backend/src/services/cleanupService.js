'use strict';
/**
 * cleanupService.js -- enforces a rolling time-to-live on sensor_readings.
 *
 * Sensor readings older than SENSOR_TTL_MINUTES (default 9) are deleted,
 * so the dashboard's "live" sensor history is always bounded to a short,
 * truly-live window. Alerts are NEVER pruned here -- incident history
 * persists indefinitely.
 *
 * Runs both:
 *   - On a recurring interval (CLEANUP_INTERVAL_SECONDS, default 60s)
 *   - Opportunistically after every new sensor write (see sensorModel.js)
 */
const prisma = require('../config/prisma');
const pool   = require('../config/db');

const TTL_MINUTES = parseInt(process.env.SENSOR_TTL_MINUTES || '9', 10);

async function pruneOldReadings() {
  const cutoff = new Date(Date.now() - TTL_MINUTES * 60000);
  try {
    const result = await prisma.sensorReading.deleteMany({
      where: { recordedAt: { lt: cutoff } },
    });
    if (result.count > 0) {
      console.log('[cleanup] Pruned ' + result.count + ' sensor reading(s) older than ' + TTL_MINUTES + 'm');
    }
    return result.count;
  } catch (e) {
    console.warn('[cleanup] Prisma prune fallback:', e.message);
    try {
      const sql = "DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '" + TTL_MINUTES + " minutes'";
      const r = await pool.query(sql);
      if (r.rowCount > 0) {
        console.log('[cleanup] Pruned ' + r.rowCount + ' sensor reading(s) (pg fallback)');
      }
      return r.rowCount;
    } catch (e2) {
      console.error('[cleanup] Prune failed entirely:', e2.message);
      return 0;
    }
  }
}

let _interval = null;

function startCleanupSchedule() {
  const seconds = parseInt(process.env.CLEANUP_INTERVAL_SECONDS || '60', 10);
  if (_interval) clearInterval(_interval);
  pruneOldReadings();
  _interval = setInterval(pruneOldReadings, seconds * 1000);
  console.log('[cleanup] Scheduled: every ' + seconds + 's, TTL ' + TTL_MINUTES + 'm');
  return _interval;
}

function stopCleanupSchedule() {
  if (_interval) { clearInterval(_interval); _interval = null; }
}

module.exports = { pruneOldReadings, startCleanupSchedule, stopCleanupSchedule, TTL_MINUTES };
