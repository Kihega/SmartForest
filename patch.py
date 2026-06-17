#!/usr/bin/env python3
"""
SmartForest — Single ENV Backend URL + 9-Minute Data TTL + Simulator Docker
==============================================================================
Run:  python single_env_patch.py /path/to/SmartForest-main

CHANGES:

  1. ONE env var for backend URL — no priority list, no hardcoding.
       Frontend : VITE_API_URL   (in frontend/.env)
       Backend  : (nothing needed — backend IS the server)
       Simulator: BACKEND_URL    (in simulator/.env)
     Whatever URL you put there — local or cloud — the app just uses it.
     No code change needed to switch between local/cloud, ever.

  2. Simulator sends realistic CHANGING readings every 3 minutes (180s)
     instead of a fixed short interval — matches real hardware reporting.

  3. Sensor readings auto-expire after 9 minutes:
       - Postgres: a scheduled cleanup deletes rows older than 9 min
       - Backend also prunes opportunistically on every sensor write
       - This keeps "live" dashboard data truly live and bounded
     Alerts table is NOT pruned (history of incidents should persist).

  4. Dockerfile for the simulator (Render Background Worker compatible)
     + full hosting instructions in SIMULATOR_HOSTING.md

  5. backend/src/services/cleanupService.js — runs the 9-min TTL sweep
     on an interval, started from index.js
"""
import os, sys

def resolve_root():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    d = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(d, 'backend', 'package.json')):
        return d
    sys.exit('Usage: python single_env_patch.py /path/to/SmartForest-main')

ROOT = resolve_root()

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK  {rel}')


# ── 1. frontend/src/config/backends.js — single VITE_API_URL ────────────────
write('frontend/src/config/backends.js', """
/**
 * backends.js — single source of truth for the backend URL (frontend).
 *
 * ONE env var, no priority list, no hardcoded fallback list:
 *   VITE_API_URL   — set this in frontend/.env to whatever is running:
 *                     local  -> http://localhost:5000/api
 *                     cloud  -> https://your-app.onrender.com/api
 *
 * The app doesn't care which one it is — it just uses whatever URL is
 * configured. Switching environments means changing ONE line in .env
 * and rebuilding (Vite bakes env vars in at build time).
 *
 * Usage:
 *   import { getAPI } from '../config/backends.js'
 *   const api = await getAPI()
 *   const res = await api.get('/alerts')
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

let _checked = false;
let _reachable = null;

async function probe() {
  try {
    await axios.get(API_URL.replace(/\\/api$/, '') + '/api/health', { timeout: 6000 });
    return true;
  } catch {
    return false;
  }
}

/** Resolves to the configured API_URL. Throws NO_BACKEND if unreachable. */
export async function resolveBackend() {
  if (_checked && _reachable) return API_URL;
  const ok = await probe();
  _checked = true;
  _reachable = ok;
  if (!ok) {
    console.warn('[Backend] Unreachable:', API_URL);
    throw new Error('NO_BACKEND');
  }
  console.info('[Backend] Connected:', API_URL);
  return API_URL;
}

/** Forces a fresh reachability check on next call. */
export function resetBackend() {
  _checked = false;
  _reachable = null;
}

/** Returns an axios instance pointed at the configured backend. */
export async function getAPI(token) {
  const baseURL = await resolveBackend();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return axios.create({ baseURL, headers });
}

/** The single configured URL (for status display / debugging). */
export const BACKEND_URL = API_URL;
""")


# ── 2. frontend/src/services/api.js — keep re-export shim ───────────────────
write('frontend/src/services/api.js', """
/**
 * api.js — re-exports from config/backends.js for backward compatibility.
 */
export { getAPI, resolveBackend, resetBackend, BACKEND_URL } from '../config/backends.js';
""")

# ── 3. frontend/src/components/BackendStatus.jsx — single URL display ───────
write('frontend/src/components/BackendStatus.jsx', """
import { useEffect, useState } from 'react'
import { resolveBackend, resetBackend, BACKEND_URL } from '../config/backends.js'

export default function BackendStatus() {
  const [status, setStatus] = useState('checking')   // 'checking' | 'online' | 'offline'

  async function check() {
    setStatus('checking')
    try {
      await resolveBackend()
      setStatus('online')
    } catch {
      setStatus('offline')
    }
  }

  useEffect(() => {
    check()
    const t = setInterval(check, 30_000)
    return () => clearInterval(t)
  }, [])

  if (status === 'online') return null

  return (
    <div style={status === 'checking' ? styles.checking : styles.offline}>
      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
        <span>{status === 'checking' ? '🟡' : '🔴'}</span>
        <div>
          <div style={{ fontWeight:700, fontSize:13 }}>
            Backend {status === 'checking' ? 'connecting…' : 'offline'}
          </div>
          {status === 'offline' && (
            <div style={{ fontSize:11, opacity:0.85, marginTop:2 }}>
              {BACKEND_URL}
            </div>
          )}
        </div>
        {status === 'offline' && (
          <button onClick={() => { resetBackend(); check() }} style={styles.retryBtn}>
            Retry
          </button>
        )}
      </div>
    </div>
  )
}

const base = {
  position:'fixed', top:12, right:12,
  padding:'10px 14px', borderRadius:8,
  color:'#fff', zIndex:9999,
  boxShadow:'0 2px 12px rgba(0,0,0,0.25)',
  maxWidth:340, fontFamily:'system-ui,sans-serif',
}
const styles = {
  checking: { ...base, background:'#d97706' },
  offline:  { ...base, background:'#dc2626' },
  retryBtn: {
    background:'rgba(255,255,255,0.25)', border:'1px solid rgba(255,255,255,0.5)',
    color:'#fff', borderRadius:6, padding:'4px 10px',
    fontSize:12, cursor:'pointer', marginLeft:4,
  },
}
""")

# ── 4. frontend/.env.example — single var ────────────────────────────────────
write('frontend/.env.example', """
# SmartForest Frontend — single backend URL.
# Set this to whichever backend you want the app to use.
# Local development:
#   VITE_API_URL=http://localhost:5000/api
# Production (Render-hosted backend):
#   VITE_API_URL=https://your-app.onrender.com/api
#
# Changing this requires a rebuild (Vite bakes env vars in at build time).
VITE_API_URL=http://localhost:5000/api
""")


# ── 5. backend/.env.example — remove BACKEND_URL_* (backend has no upstream) ─
write('backend/.env.example', """
PORT=5000
NODE_ENV=development

# ── Supabase ─────────────────────────────────────────────────────────────────
SUPABASE_URL=https://[REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# ── Database (Supabase POOLER — no direct host needed) ───────────────────────
# Transaction pooler — runtime app queries (port 6543)
DATABASE_URL=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
# Session pooler — prisma db push / migrate (port 5432)
DATABASE_URL_DIRECT=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres

# ── App ───────────────────────────────────────────────────────────────────────
JWT_SECRET=change-this-to-a-long-random-secret
FRONTEND_URL=http://localhost:5173

# ── MQTT ─────────────────────────────────────────────────────────────────────
MQTT_BROKER=mqtt://localhost:1883
MQTT_TOPIC=forest/sensor/data

# ── Alert thresholds ─────────────────────────────────────────────────────────
SOUND_THRESHOLD_DB=80
TEMP_THRESHOLD_C=55
DEDUP_MINUTES=5

# ── Sensor data retention (TTL) ───────────────────────────────────────────────
# Sensor readings older than this are auto-deleted. Alerts are kept forever.
SENSOR_TTL_MINUTES=9
CLEANUP_INTERVAL_SECONDS=60
""")


# ── 6. backend/src/services/cleanupService.js — 9-minute TTL sweep ───────────
CLEANUP_SERVICE_JS = r''''use strict';
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
'''
write('backend/src/services/cleanupService.js', CLEANUP_SERVICE_JS)


# ── 7. backend/src/models/sensorModel.js — opportunistic prune on write ──────
SENSOR_MODEL_JS = r'''
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
'''
write('backend/src/models/sensorModel.js', SENSOR_MODEL_JS)


# ── 8. backend/src/index.js — start cleanup schedule on boot ─────────────────
INDEX_JS = r'''const express      = require('express');
const cors         = require('cors');
const dotenv       = require('dotenv');
const { connectMQTT } = require('./services/mqttService');
const { startCleanupSchedule } = require('./services/cleanupService');
const errorHandler = require('./middleware/errorHandler');

dotenv.config();

const app  = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/alerts',  require('./routes/alerts'));
app.use('/api/sensors', require('./routes/sensors'));
app.use('/api/auth',    require('./routes/auth'));
app.use('/api/devices', require('./routes/devices'));
app.use('/api/admin',   require('./routes/admin'));

// Health check -- reports which Supabase project this deployment uses,
// plus the active sensor-data retention window.
app.get('/api/health', (_req, res) => {
  let supabaseRef = 'NOT_CONFIGURED';
  try {
    const url = process.env.SUPABASE_URL || '';
    const match = url.match(/https:\/\/([a-z0-9]+)\.supabase\.co/i);
    supabaseRef = match ? match[1] : (url ? 'UNRECOGNISED_URL_FORMAT' : 'NOT_SET');
  } catch (_) { /* ignore */ }

  res.json({
    status          : 'ok',
    timestamp       : new Date().toISOString(),
    supabaseProject : supabaseRef,
    nodeEnv         : process.env.NODE_ENV || 'development',
    hasServiceKey   : !!process.env.SUPABASE_SERVICE_KEY,
    hasDbUrl        : !!process.env.DATABASE_URL,
    sensorTtlMinutes: parseInt(process.env.SENSOR_TTL_MINUTES || '9', 10),
  });
});

app.use(errorHandler);

let server;
if (process.env.NODE_ENV !== 'test') {
  connectMQTT();
  startCleanupSchedule();   // begin the 9-minute sensor-data TTL sweep
  server = app.listen(PORT, () => {
    console.log(`SmartForest backend running on http://localhost:${PORT}`);
    console.log(`Supabase project: ${(process.env.SUPABASE_URL || 'NOT SET')}`);
  });
}

module.exports = { app, server };
'''
write('backend/src/index.js', INDEX_JS)


# ── 9. backend/jest.setup.js — add cleanupService mock (avoid real timers) ───
jest_path = os.path.join(ROOT, 'backend', 'jest.setup.js')
if os.path.isfile(jest_path):
    src = open(jest_path, encoding='utf-8').read()
    addition = """
// -- cleanupService -- mocked so tests never start real intervals
jest.mock('./src/services/cleanupService', () => ({
  pruneOldReadings    : jest.fn().mockResolvedValue(0),
  startCleanupSchedule: jest.fn(),
  stopCleanupSchedule : jest.fn(),
  TTL_MINUTES: 9,
}));
"""
    if 'cleanupService' not in src:
        src = src.rstrip() + '\n' + addition
        with open(jest_path, 'w', encoding='utf-8') as f:
            f.write(src)
        print('  OK  backend/jest.setup.js  (added cleanupService mock)')
    else:
        print('  SKIP backend/jest.setup.js  (cleanupService mock already present)')
else:
    print('  SKIP backend/jest.setup.js  (file not found)')


# ── 10. simulator/mqtt_simulator.py — single BACKEND_URL, 3-min interval ─────
SIMULATOR_PY = r'''#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates real hardware sensor units. Sends a NEW reading every 3 minutes
# (180s) by default, with realistic parameter drift between readings so
# values change gradually rather than jumping randomly each time.
#
# Backend URL -- SINGLE env var, no priority list:
#   BACKEND_URL=http://localhost:5000        (local)
#   BACKEND_URL=https://your-app.onrender.com (cloud)
# Whichever one is set is what the simulator uses. No code change needed
# to switch between local and cloud -- just change .env and restart.
#
# Hardware ID convention:
#   Real hardware : smf-m01a (microphone), smf-f01a (flame)
#   Simulator     : smt-m01a (microphone), smt-f01a (flame)
#
# Usage:
#   pip install -r requirements.txt
#   python mqtt_simulator.py             # run with defaults (180s interval)
#   python mqtt_simulator.py --stop      # graceful stop
#   python mqtt_simulator.py --interval 30 --spike 0.3   # faster for testing
#   USE_REAL_IDS=true python mqtt_simulator.py
#
# Env vars (set in simulator/.env):
#   BACKEND_URL         single backend URL -- local or cloud, doesn't matter
#   MQTT_BROKER_HOST    default: localhost (optional -- HTTP works standalone)
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   SEND_INTERVAL       default: 180 (seconds -- 3 minutes, matches real HW)
#   SPIKE_CHANCE        default: 0.20
#   USE_REAL_IDS        default: false

import json, random, time, os, sys, argparse, signal, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# -- Optional MQTT (HTTP-only mode works fine without a broker) --------------
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

# -- Load .env if python-dotenv is available ----------------------------------
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f'[SIM] Loaded env: {env_file}')
except ImportError:
    pass

# -- Config: ONE backend URL, no fallback list --------------------------------
BACKEND_URL  = os.getenv('BACKEND_URL', 'http://localhost:5000').rstrip('/')
BROKER       = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC', 'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL', 180))   # 3 minutes, matches real HW
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE', 0.20))
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
SENTINEL     = Path(__file__).parent / 'STOP_SIMULATOR'

PREFIX    = 'smf' if USE_REAL_IDS else 'smt'
MIC_IDS   = [f'{PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_IDS = [f'{PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
    {'zone': 'Kibiti-West',  'lat': -7.80, 'lng': 38.82},
]

# -- Drifting state per device, so each new reading shifts gradually ---------
# instead of jumping randomly -- mimics real sensor behaviour over time.
_state = {}

def _drift(device_id, base, lo, hi, max_step):
    prev = _state.get(device_id, base)
    step = random.uniform(-max_step, max_step)
    val  = max(lo, min(hi, prev + step))
    _state[device_id] = val
    return round(val, 2)

# -- Backend health probe ------------------------------------------------------
def probe_backend(timeout=5):
    try:
        req = urllib.request.urlopen(BACKEND_URL + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception as e:
        print(f'[SIM] Backend probe failed: {e}')
        return False

# -- Payload generators (with gradual drift) ----------------------------------
def make_mic(spike):
    z = random.choice(ZONES)
    device = random.choice(MIC_IDS)
    if spike:
        db = round(random.uniform(82, 98), 2)
    else:
        db = _drift(device, 35, 18, 65, 6)
    return {
        'device_id'    : device,
        'sensor_type'  : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'    : datetime.now(timezone.utc).isoformat(),
        'zone'         : z['zone'],
        'latitude'     : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'    : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'     : db,
    }

def make_flame(spike):
    z = random.choice(ZONES)
    device = random.choice(FLAME_IDS)
    if spike:
        temp = round(random.uniform(58, 95), 2)
    else:
        temp = _drift(device, 27, 20, 42, 3)
    return {
        'device_id'      : device,
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : z['zone'],
        'latitude'       : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : bool(spike),
        'temperature_c'  : temp,
    }

# -- HTTP POST to backend ------------------------------------------------------
def post_reading(payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            BACKEND_URL + '/api/sensors',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=8)
        return True
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')
        return False

# -- MQTT callbacks (optional) -------------------------------------------------
_running = True

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print(f'[MQTT] Connected: {BROKER}:{PORT}  topic: {TOPIC}')
    else:
        print(f'[MQTT] Connect failed rc={rc}')

def on_disconnect(client, userdata, flags, rc, props=None):
    if rc != 0:
        print(f'[MQTT] Disconnected rc={rc} -- will retry on next publish')

def graceful_stop(sig, frame):
    global _running
    print('\\n[SIM] Stopping...')
    _running = False

# -- CLI -----------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Simulator')
    p.add_argument('--stop',      action='store_true', help='Stop a running instance')
    p.add_argument('--interval',  type=float, default=INTERVAL)
    p.add_argument('--spike',     type=float, default=SPIKE_CHANCE)
    p.add_argument('--real-hw',   action='store_true', help='Use smf-* IDs')
    p.add_argument('--http-only', action='store_true', help='Skip MQTT entirely')
    return p.parse_args()

# -- Main ------------------------------------------------------------------------
def main():
    global _running, USE_REAL_IDS, MIC_IDS, FLAME_IDS, PREFIX, INTERVAL, SPIKE_CHANCE

    args = parse_args()

    if args.stop:
        SENTINEL.touch()
        print(f'[SIM] Stop signal written: {SENTINEL}')
        return

    INTERVAL     = args.interval
    SPIKE_CHANCE = args.spike
    if args.real_hw:
        USE_REAL_IDS = True
        PREFIX    = 'smf'
        MIC_IDS   = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_IDS = [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    if SENTINEL.exists():
        SENTINEL.unlink()

    hw_label = 'REAL HW' if USE_REAL_IDS else 'SIMULATOR'
    print('=' * 60)
    print('  SmartForest IoT Simulator')
    print('=' * 60)
    print(f'  Mode      : {hw_label}')
    print(f'  Backend   : {BACKEND_URL}   (single env var: BACKEND_URL)')
    print(f'  MIC IDs   : {MIC_IDS}')
    print(f'  FLAME IDs : {FLAME_IDS}')
    print(f'  Interval  : {INTERVAL}s ({INTERVAL/60:.1f} min)  |  Spike: {int(SPIKE_CHANCE*100)}%')
    print()

    if not probe_backend():
        print(f'[SIM] WARNING: backend not reachable at {BACKEND_URL}')
        print('[SIM] Will keep trying to POST each cycle -- check BACKEND_URL in .env')
    else:
        print(f'[SIM] Backend reachable: {BACKEND_URL}')

    client = None
    if HAS_MQTT and not args.http_only:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect    = on_connect
            client.on_disconnect = on_disconnect
            client.connect(BROKER, PORT, keepalive=60)
            client.loop_start()
            time.sleep(1.0)
        except Exception as e:
            print(f'[MQTT] Cannot connect: {e} -- continuing HTTP-only')
            client = None
    elif not HAS_MQTT:
        print('[SIM] paho-mqtt not installed -- running HTTP-only')

    print()
    print('  Ctrl+C  or  python mqtt_simulator.py --stop  to exit')
    print('-' * 60)

    reads = 0
    alerts_sent = 0

    while _running:
        if SENTINEL.exists():
            SENTINEL.unlink()
            print('[SIM] Stop sentinel detected -- exiting cleanly')
            break

        spike   = random.random() < SPIKE_CHANCE
        use_mic = reads % 2 == 0
        payload = make_mic(spike) if use_mic else make_flame(spike)

        if client:
            try:
                client.publish(TOPIC, json.dumps(payload))
            except Exception as e:
                print(f'  [MQTT] Publish failed: {e}')

        ok = post_reading(payload)

        reads += 1
        if spike:
            alerts_sent += 1

        ts   = datetime.now().strftime('%H:%M:%S')
        d    = payload['device_id']
        zone = payload['zone']
        if use_mic:
            reading = f"{payload['sound_db']} dB"
            kind    = 'ALERT-LOG' if spike else 'mic-ok  '
        else:
            reading = f"{payload['temperature_c']} C"
            kind    = 'ALERT-FIRE' if spike else 'flame-ok'

        flag   = '\U0001f6a8' if spike else '  '
        status = 'OK' if ok else 'FAIL'
        print(f'{ts} {flag} {kind}  {d:<12}  {zone:<14}  {reading:<10}  http:{status}  [r:{reads} a:{alerts_sent}]')

        time.sleep(INTERVAL)

    print(f'\\n[SIM] Stopped. Total readings: {reads} | Alerts: {alerts_sent}')
    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
'''
write('simulator/mqtt_simulator.py', SIMULATOR_PY)


# ── 11. simulator/Dockerfile — for Render Background Worker ─────────────────
write('simulator/Dockerfile', """
FROM python:3.11-slim

WORKDIR /app

# System deps for paho-mqtt / dotenv (minimal, slim image)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No EXPOSE needed -- this is a worker, not a web service.
# It only makes outbound HTTP/MQTT calls to BACKEND_URL.
CMD ["python", "mqtt_simulator.py"]
""")

# ── 12. simulator/.env.example — single BACKEND_URL ──────────────────────────
write('simulator/.env.example', """
# SmartForest Simulator -- single backend URL.
# Doesn't matter if it's local or cloud -- just point it at whatever
# backend you want this simulator instance to feed data into.
#
# Local development:
#   BACKEND_URL=http://localhost:5000
# Cloud (Render-hosted backend):
#   BACKEND_URL=https://your-backend.onrender.com
BACKEND_URL=http://localhost:5000

# Optional MQTT (simulator works fine over HTTP alone if no broker is set up)
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC=forest/sensor/data

# Reporting interval -- 180s (3 minutes) matches real hardware reporting rate
SEND_INTERVAL=180
SPIKE_CHANCE=0.20
USE_REAL_IDS=false
""")

# ── 13. simulator/requirements.txt ───────────────────────────────────────────
write('simulator/requirements.txt', """
paho-mqtt>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
""")


# ── 14. SIMULATOR_HOSTING.md — full Render Background Worker walkthrough ─────
write('SIMULATOR_HOSTING.md', """# Hosting the Simulator on Render

**Yes — Dockerize it and run it as a Render Background Worker.**
A Background Worker is exactly right here: the simulator only makes
*outbound* HTTP/MQTT calls to your backend, it never needs to receive
inbound traffic or have a public URL. Render's free-tier Background
Workers fit this perfectly (no idle spin-down issue like free Web
Services have, since there's no HTTP server to spin down).

## What you get

```
simulator/
  Dockerfile          <- builds the worker image
  mqtt_simulator.py   <- the simulator itself
  requirements.txt
  .env.example
```

## Step-by-step: Deploy to Render

1. **Push the `simulator/` folder to your GitHub repo** (already part of
   the SmartForest monorepo — Render can build from a subdirectory).

2. **Render Dashboard → New → Background Worker**

3. **Connect your repo**, then configure:
   - **Root Directory**: `simulator`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `simulator/Dockerfile` (or just `Dockerfile` if
     root directory is already `simulator`)

4. **Environment variables** (Render Dashboard → your worker → Environment):
   ```
   BACKEND_URL=https://your-backend.onrender.com
   SEND_INTERVAL=180
   SPIKE_CHANCE=0.20
   USE_REAL_IDS=false
   ```
   That's it — just `BACKEND_URL`. Point it at your backend's Render URL
   (or any backend URL — local or cloud, the simulator doesn't care).

5. **Deploy.** Render builds the Docker image and starts the worker.
   Check the **Logs** tab — you should see:
   ```
   [SIM] Backend reachable: https://your-backend.onrender.com
   12:03:01    mic-ok    smt-m01a      Kibiti-North    35.2 dB    http:OK  [r:1 a:0]
   ```

6. **To stop it**: Render Dashboard → your worker → **Suspend**.
   (The `--stop` sentinel-file approach is for local/manual runs; on
   Render, just suspend/resume the worker from the dashboard.)

## Local run (no Docker needed)

```bash
cd simulator
pip install -r requirements.txt
cp .env.example .env          # edit BACKEND_URL if needed
python mqtt_simulator.py
```

## Local run (with Docker, to test the exact image Render will use)

```bash
cd simulator
docker build -t smartforest-simulator .
docker run --rm \\
  -e BACKEND_URL=http://host.docker.internal:5000 \\
  smartforest-simulator
```
(`host.docker.internal` lets the container reach your locally-running
backend; on Linux you may need `--add-host=host.docker.internal:host-gateway`.)

## Why a Background Worker, not a Web Service

A Web Service on Render's free tier spins down after ~15 minutes of no
inbound HTTP traffic, and the simulator never receives inbound traffic —
it only sends data out. Deploying it as a Web Service would cause Render
to repeatedly spin it down for "inactivity" even while it's actively
posting sensor data, killing your data flow. A Background Worker has no
such inbound-traffic requirement and just keeps running.
""")


# ── 15. simulator/tests/test_simulator.py — updated for new simulator ────────
TEST_SIM_PY = r'''# SmartForest Simulator Tests
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('BACKEND_URL',    'http://localhost:5000')
os.environ.setdefault('MQTT_BROKER_HOST', 'localhost')
os.environ.setdefault('SEND_INTERVAL',  '180')
os.environ.setdefault('SPIKE_CHANCE',   '0.20')

import mqtt_simulator as sim


class TestPayloadGenerators:
    def test_mic_normal_payload_schema(self):
        p = sim.make_mic(spike=False)
        assert 'device_id'   in p
        assert 'sensor_type' in p
        assert 'zone'        in p
        assert 'sound_db'    in p
        assert 'latitude'    in p
        assert 'longitude'   in p
        assert 'timestamp'   in p
        assert p['sensor_type'] == 'microphone'

    def test_mic_spike_high_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=True)
            assert p['sound_db'] >= 80

    def test_mic_normal_low_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=False)
            assert p['sound_db'] < 80

    def test_flame_normal_payload_schema(self):
        p = sim.make_flame(spike=False)
        assert 'device_id'      in p
        assert 'sensor_type'    in p
        assert 'flame_detected' in p
        assert 'temperature_c'  in p
        assert p['sensor_type'] == 'flame'
        assert p['flame_detected'] == False

    def test_flame_spike_detected(self):
        p = sim.make_flame(spike=True)
        assert p['flame_detected'] == True
        assert p['temperature_c'] >= 55

    def test_payload_json_serializable(self):
        for fn, s in [(sim.make_mic, False), (sim.make_mic, True),
                      (sim.make_flame, False), (sim.make_flame, True)]:
            p = fn(s)
            j = json.dumps(p)
            assert isinstance(j, str)
            assert len(j) > 10

    def test_device_ids_format(self):
        for _ in range(10):
            mic_p = sim.make_mic(False)
            assert mic_p['device_id'].startswith(sim.PREFIX + '-m')
            flm_p = sim.make_flame(False)
            assert flm_p['device_id'].startswith(sim.PREFIX + '-f')

    def test_zone_is_valid(self):
        valid_zones = {z['zone'] for z in sim.ZONES}
        for _ in range(10):
            p = sim.make_mic(False)
            assert p['zone'] in valid_zones

    def test_coordinates_near_kibiti(self):
        for _ in range(10):
            p = sim.make_mic(False)
            assert -9.0 < p['latitude']  < -6.5
            assert  37.5 < p['longitude'] < 40.5


class TestDrift:
    def test_drift_stays_within_bounds(self):
        sim._state.clear()
        for _ in range(50):
            p = sim.make_mic(spike=False)
            assert 18 <= p['sound_db'] <= 65

    def test_drift_changes_gradually(self):
        sim._state.clear()
        device = sim.MIC_IDS[0]
        sim._state[device] = 35
        val1 = sim._drift(device, 35, 18, 65, 6)
        val2 = sim._drift(device, 35, 18, 65, 6)
        # consecutive drift steps should differ by at most 2x max_step
        assert abs(val2 - val1) <= 12


class TestSingleBackendUrl:
    def test_backend_url_is_single_string(self):
        assert isinstance(sim.BACKEND_URL, str)
        assert sim.BACKEND_URL.startswith('http')

    def test_no_priority_list_attribute(self):
        # Ensure the old multi-candidate design is gone
        assert not hasattr(sim, 'BACKEND_CANDIDATES')

    def test_probe_returns_bool(self):
        old_url = sim.BACKEND_URL
        sim.BACKEND_URL = 'http://localhost:19999'
        result = sim.probe_backend(timeout=1)
        sim.BACKEND_URL = old_url
        assert result is False


class TestSentinel:
    def test_sentinel_path_is_in_simulator_dir(self):
        import pathlib
        expected_dir = pathlib.Path(__file__).parent.parent
        assert sim.SENTINEL.parent == expected_dir


class TestInterval:
    def test_default_interval_is_three_minutes(self):
        assert sim.INTERVAL == 180
'''
write('simulator/tests/test_simulator.py', TEST_SIM_PY)


# ── 16. database/migrations/007_sensor_ttl_index.sql ──────────────────────────
write('database/migrations/007_sensor_ttl_index.sql', """
-- MIGRATION 007: index to make the 9-minute TTL cleanup sweep fast.
-- Run in Supabase SQL Editor (or it's covered automatically by
-- `npx prisma db push` if you're using the Prisma schema, since the
-- index already exists there as idx_sr_time).
--
-- This is the manual-SQL equivalent fallback for the TTL cleanup query:
--   DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '9 minutes';

CREATE INDEX IF NOT EXISTS idx_sensor_readings_recorded_at
  ON sensor_readings (recorded_at);

-- Optional: enable pg_cron for a DB-side scheduled sweep as a second
-- layer of defense, independent of whether the Node backend is awake.
-- Uncomment if your Supabase project has pg_cron enabled
-- (Database -> Extensions -> pg_cron):
--
-- SELECT cron.schedule(
--   'smartforest_sensor_ttl_sweep',
--   '* * * * *',  -- every minute
--   $$DELETE FROM sensor_readings WHERE recorded_at < NOW() - INTERVAL '9 minutes'$$
-- );
""")


# ── Final summary ─────────────────────────────────────────────────────────
print()
print('=' * 64)
print('  single_env_patch applied!')
print('=' * 64)
print()
print('1. SINGLE ENV VAR (no priority lists, no hardcoding):')
print('     Frontend : VITE_API_URL     (frontend/.env)')
print('     Simulator: BACKEND_URL      (simulator/.env)')
print('   Set it to local OR cloud -- the app does not care which.')
print()
print('2. SIMULATOR now sends a NEW reading every 3 minutes (180s),')
print('   with realistic gradual drift between readings instead of')
print('   random jumps -- matches real hardware behaviour.')
print()
print('3. SENSOR DATA TTL: readings older than 9 minutes are deleted')
print('   automatically (cleanupService runs every 60s + opportunistic')
print('   prune after every write). Alerts are NEVER pruned -- incident')
print('   history persists. Configurable via SENSOR_TTL_MINUTES.')
print()
print('4. SIMULATOR CAN BE DOCKERIZED AND HOSTED ON RENDER -- YES.')
print('   Deploy as a Render BACKGROUND WORKER (not Web Service), since')
print('   it only sends outbound data and never needs a public URL.')
print('   Full steps in SIMULATOR_HOSTING.md.')
print()
print('NEXT STEPS:')
print()
print('  A) Update frontend/.env:')
print('       VITE_API_URL=https://your-backend.onrender.com/api')
print('     (or http://localhost:5000/api for local dev)')
print('     Rebuild/redeploy after changing this.')
print()
print('  B) Update backend/.env (add if missing):')
print('       SENSOR_TTL_MINUTES=9')
print('       CLEANUP_INTERVAL_SECONDS=60')
print()
print('  C) Update simulator/.env:')
print('       BACKEND_URL=https://your-backend.onrender.com')
print('       SEND_INTERVAL=180')
print()
print('  D) Push schema (adds the TTL-supporting index):')
print('       cd backend && npx prisma db push')
print()
print('  E) Deploy simulator to Render as a Background Worker:')
print('       Root Directory : simulator')
print('       Environment    : Docker')
print('       Env var        : BACKEND_URL=<your backend URL>')
print('     See SIMULATOR_HOSTING.md for full walkthrough.')
print()
print('  F) Run tests:')
print('       cd backend && npm test')
print('       cd simulator && pytest tests/ -v')
print()
print('Done!')

