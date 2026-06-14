#!/usr/bin/env python3
"""
patch_sprint1.py — Sprint 1: Full backend wiring + simulator upgrade
Actions:
  1. Remove frontend/Dockerfile and root vercel.json (not needed)
  2. Implement sensorModel.js, alertModel.js, userModel.js
  3. Wire all routes to real DB models
  4. Implement alertService.js (threshold check + deduplication)
  5. Wire mqttService.js to models + alertService
  6. Implement errorHandler.js middleware
  7. Upgrade simulator with verbose logging and retry logic
  8. Fix docker-compose.yml (remove frontend service, keep backend+mqtt only)
  9. Update tests to work with real DB responses
  10. Update migrations: fix order (users before alerts)

Run from SmartForest ROOT: python3 patch_sprint1.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def overwrite(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("  [UPDATE] " + path)

def delete(path):
    full = os.path.join(ROOT, path)
    if os.path.exists(full):
        os.remove(full)
        print("  [DELETE] " + path)
    else:
        print("  [SKIP]   " + path + " (already gone)")

if not os.path.isdir(os.path.join(ROOT, "backend")):
    print("ERROR: Run from SmartForest ROOT folder.")
    exit(1)

BT = chr(96)

# ─────────────────────────────────────────────────────────────
# 1. REMOVE FRONTEND DOCKER FILES
# ─────────────────────────────────────────────────────────────
print("\n[1/10] Removing frontend Docker files...")
delete("frontend/Dockerfile")
delete("vercel.json")  # root-level duplicate — frontend/vercel.json is the real one

# ─────────────────────────────────────────────────────────────
# 2. DATABASE MIGRATIONS — fix execution order in comments
# ─────────────────────────────────────────────────────────────
print("\n[2/10] Fixing database migration order...")

overwrite("database/migrations/001_create_users.sql", (
    "-- MIGRATION 001: Create users table\n"
    "-- Run this FIRST in Supabase SQL Editor\n"
    "-- (alerts table references users.id so users must exist first)\n\n"
    "CREATE TABLE IF NOT EXISTS users (\n"
    "  id         SERIAL PRIMARY KEY,\n"
    "  name       VARCHAR(100),\n"
    "  email      VARCHAR(100)  UNIQUE NOT NULL,\n"
    "  role       VARCHAR(20)   DEFAULT 'ranger',\n"
    "  created_at TIMESTAMPTZ   DEFAULT NOW()\n"
    ");\n"
))

overwrite("database/migrations/002_create_sensor_readings.sql", (
    "-- MIGRATION 002: Create sensor_readings table\n"
    "-- Run SECOND in Supabase SQL Editor\n\n"
    "CREATE TABLE IF NOT EXISTS sensor_readings (\n"
    "  id          SERIAL PRIMARY KEY,\n"
    "  device_id   VARCHAR(50)      NOT NULL,\n"
    "  zone        VARCHAR(100),\n"
    "  latitude    DOUBLE PRECISION,\n"
    "  longitude   DOUBLE PRECISION,\n"
    "  sound_db    NUMERIC(5,2),\n"
    "  vibration   NUMERIC(5,2),\n"
    "  is_alert    BOOLEAN          DEFAULT FALSE,\n"
    "  recorded_at TIMESTAMPTZ      DEFAULT NOW()\n"
    ");\n\n"
    "CREATE INDEX IF NOT EXISTS idx_sensor_readings_device\n"
    "  ON sensor_readings(device_id);\n"
    "CREATE INDEX IF NOT EXISTS idx_sensor_readings_time\n"
    "  ON sensor_readings(recorded_at DESC);\n"
))

overwrite("database/migrations/003_create_alerts.sql", (
    "-- MIGRATION 003: Create alerts table\n"
    "-- Run THIRD in Supabase SQL Editor\n"
    "-- (references users.id — run migration 001 first)\n\n"
    "CREATE TABLE IF NOT EXISTS alerts (\n"
    "  id          SERIAL PRIMARY KEY,\n"
    "  device_id   VARCHAR(50),\n"
    "  zone        VARCHAR(100),\n"
    "  latitude    DOUBLE PRECISION,\n"
    "  longitude   DOUBLE PRECISION,\n"
    "  sound_db    NUMERIC(5,2),\n"
    "  vibration   NUMERIC(5,2),\n"
    "  status      VARCHAR(20)      DEFAULT 'unresolved',\n"
    "  resolved_by INTEGER          REFERENCES users(id),\n"
    "  created_at  TIMESTAMPTZ      DEFAULT NOW()\n"
    ");\n\n"
    "CREATE INDEX IF NOT EXISTS idx_alerts_status\n"
    "  ON alerts(status);\n"
    "CREATE INDEX IF NOT EXISTS idx_alerts_time\n"
    "  ON alerts(created_at DESC);\n"
))

overwrite("database/seeds/dev_seed.sql", (
    "-- DEV SEED: Sample data for local testing\n"
    "-- Run AFTER all 3 migrations in Supabase SQL Editor\n\n"
    "INSERT INTO users (name, email, role) VALUES\n"
    "  ('Admin Ranger', 'admin@smartforest.tz', 'admin'),\n"
    "  ('John Ranger',  'john@smartforest.tz',  'ranger')\n"
    "ON CONFLICT (email) DO NOTHING;\n\n"
    "INSERT INTO sensor_readings\n"
    "  (device_id, zone, latitude, longitude, sound_db, vibration, is_alert)\n"
    "VALUES\n"
    "  ('SENSOR-001', 'Kibiti-North', -7.72,  38.95, 45.2, 2.1, FALSE),\n"
    "  ('SENSOR-002', 'Kibiti-South', -7.85,  38.88, 91.5, 8.3, TRUE),\n"
    "  ('SENSOR-003', 'Kibiti-East',  -7.78,  39.05, 33.0, 1.5, FALSE)\n"
    "ON CONFLICT DO NOTHING;\n\n"
    "INSERT INTO alerts\n"
    "  (device_id, zone, latitude, longitude, sound_db, vibration, status)\n"
    "VALUES\n"
    "  ('SENSOR-002', 'Kibiti-South', -7.85, 38.88, 91.5, 8.3, 'unresolved')\n"
    "ON CONFLICT DO NOTHING;\n"
))

# ─────────────────────────────────────────────────────────────
# 3. SENSOR MODEL
# ─────────────────────────────────────────────────────────────
print("\n[3/10] Implementing sensorModel.js...")

overwrite("backend/src/models/sensorModel.js", (
    "const pool = require('../config/db');\n\n"
    "const sensorModel = {\n\n"
    "  // Insert a new sensor reading\n"
    "  async saveReading(data) {\n"
    "    const { device_id, zone, latitude, longitude,\n"
    "            sound_db, vibration, is_alert } = data;\n"
    "    const result = await pool.query(\n"
    "      `INSERT INTO sensor_readings\n"
    "         (device_id, zone, latitude, longitude, sound_db, vibration, is_alert)\n"
    "       VALUES ($1, $2, $3, $4, $5, $6, $7)\n"
    "       RETURNING *`,\n"
    "      [device_id, zone, latitude, longitude,\n"
    "       sound_db, vibration, is_alert || false]\n"
    "    );\n"
    "    return result.rows[0];\n"
    "  },\n\n"
    "  // Get all sensor readings ordered by newest first\n"
    "  async getAll(limit = 100) {\n"
    "    const result = await pool.query(\n"
    "      'SELECT * FROM sensor_readings ORDER BY recorded_at DESC LIMIT $1',\n"
    "      [limit]\n"
    "    );\n"
    "    return result.rows;\n"
    "  },\n\n"
    "  // Get the latest reading per device_id\n"
    "  async getLive() {\n"
    "    const result = await pool.query(\n"
    "      `SELECT DISTINCT ON (device_id)\n"
    "              id, device_id, zone, latitude, longitude,\n"
    "              sound_db, vibration, is_alert, recorded_at\n"
    "       FROM   sensor_readings\n"
    "       ORDER  BY device_id, recorded_at DESC`\n"
    "    );\n"
    "    return result.rows;\n"
    "  },\n\n"
    "  // Get readings for a specific device\n"
    "  async getByDevice(device_id, limit = 50) {\n"
    "    const result = await pool.query(\n"
    "      `SELECT * FROM sensor_readings\n"
    "       WHERE  device_id = $1\n"
    "       ORDER  BY recorded_at DESC LIMIT $2`,\n"
    "      [device_id, limit]\n"
    "    );\n"
    "    return result.rows;\n"
    "  },\n\n"
    "};\n\n"
    "module.exports = sensorModel;\n"
))

# ─────────────────────────────────────────────────────────────
# 4. ALERT MODEL
# ─────────────────────────────────────────────────────────────
print("\n[4/10] Implementing alertModel.js...")

overwrite("backend/src/models/alertModel.js", (
    "const pool = require('../config/db');\n\n"
    "const alertModel = {\n\n"
    "  // Insert a new alert\n"
    "  async create(data) {\n"
    "    const { device_id, zone, latitude,\n"
    "            longitude, sound_db, vibration } = data;\n"
    "    const result = await pool.query(\n"
    "      `INSERT INTO alerts\n"
    "         (device_id, zone, latitude, longitude, sound_db, vibration)\n"
    "       VALUES ($1, $2, $3, $4, $5, $6)\n"
    "       RETURNING *`,\n"
    "      [device_id, zone, latitude, longitude, sound_db, vibration]\n"
    "    );\n"
    "    return result.rows[0];\n"
    "  },\n\n"
    "  // Get all alerts ordered by newest first\n"
    "  async getAll(limit = 100) {\n"
    "    const result = await pool.query(\n"
    "      `SELECT * FROM alerts\n"
    "       ORDER BY created_at DESC LIMIT $1`,\n"
    "      [limit]\n"
    "    );\n"
    "    return result.rows;\n"
    "  },\n\n"
    "  // Get single alert by id\n"
    "  async getById(id) {\n"
    "    const result = await pool.query(\n"
    "      'SELECT * FROM alerts WHERE id = $1',\n"
    "      [id]\n"
    "    );\n"
    "    return result.rows[0] || null;\n"
    "  },\n\n"
    "  // Get all unresolved alerts\n"
    "  async getUnresolved() {\n"
    "    const result = await pool.query(\n"
    "      `SELECT * FROM alerts\n"
    "       WHERE  status = 'unresolved'\n"
    "       ORDER  BY created_at DESC`\n"
    "    );\n"
    "    return result.rows;\n"
    "  },\n\n"
    "  // Count unresolved alerts (for navbar badge)\n"
    "  async countUnresolved() {\n"
    "    const result = await pool.query(\n"
    "      `SELECT COUNT(*) FROM alerts WHERE status = 'unresolved'`\n"
    "    );\n"
    "    return parseInt(result.rows[0].count, 10);\n"
    "  },\n\n"
    "  // Mark alert as resolved\n"
    "  async resolve(id) {\n"
    "    const result = await pool.query(\n"
    "      `UPDATE alerts SET status = 'resolved'\n"
    "       WHERE id = $1 RETURNING *`,\n"
    "      [id]\n"
    "    );\n"
    "    return result.rows[0] || null;\n"
    "  },\n\n"
    "  // Check if same device alerted recently (deduplication)\n"
    "  // Returns true if an alert exists for this device in last N minutes\n"
    "  async recentlyAlerted(device_id, minutes = 5) {\n"
    "    const result = await pool.query(\n"
    "      `SELECT id FROM alerts\n"
    "       WHERE  device_id = $1\n"
    "       AND    created_at > NOW() - INTERVAL '$2 minutes'\n"
    "       LIMIT  1`,\n"
    "      [device_id, minutes]\n"
    "    );\n"
    "    return result.rows.length > 0;\n"
    "  },\n\n"
    "};\n\n"
    "module.exports = alertModel;\n"
))

# ─────────────────────────────────────────────────────────────
# 5. USER MODEL
# ─────────────────────────────────────────────────────────────
print("\n[5/10] Implementing userModel.js...")

overwrite("backend/src/models/userModel.js", (
    "const pool = require('../config/db');\n\n"
    "const userModel = {\n\n"
    "  // Get user by email\n"
    "  async getByEmail(email) {\n"
    "    const result = await pool.query(\n"
    "      'SELECT * FROM users WHERE email = $1',\n"
    "      [email]\n"
    "    );\n"
    "    return result.rows[0] || null;\n"
    "  },\n\n"
    "  // Get user by id\n"
    "  async getById(id) {\n"
    "    const result = await pool.query(\n"
    "      'SELECT * FROM users WHERE id = $1',\n"
    "      [id]\n"
    "    );\n"
    "    return result.rows[0] || null;\n"
    "  },\n\n"
    "  // Create new user profile (linked to Supabase Auth)\n"
    "  async create(data) {\n"
    "    const { name, email, role } = data;\n"
    "    const result = await pool.query(\n"
    "      `INSERT INTO users (name, email, role)\n"
    "       VALUES ($1, $2, $3)\n"
    "       ON CONFLICT (email) DO UPDATE\n"
    "         SET name = EXCLUDED.name\n"
    "       RETURNING *`,\n"
    "      [name, email, role || 'ranger']\n"
    "    );\n"
    "    return result.rows[0];\n"
    "  },\n\n"
    "};\n\n"
    "module.exports = userModel;\n"
))

# ─────────────────────────────────────────────────────────────
# 6. ALERT SERVICE (threshold + deduplication)
# ─────────────────────────────────────────────────────────────
print("\n[6/10] Implementing alertService.js...")

overwrite("backend/src/services/alertService.js", (
    "const alertModel  = require('../models/alertModel');\n"
    "require('dotenv').config();\n\n"
    "const SOUND_THRESHOLD     = parseFloat(process.env.SOUND_THRESHOLD_DB || 80);\n"
    "const VIBRATION_THRESHOLD = parseFloat(process.env.VIBRATION_THRESHOLD || 7);\n"
    "const DEDUP_MINUTES       = 5; // suppress duplicate alerts within 5 minutes\n\n"
    "const alertService = {\n\n"
    "  // Evaluate a sensor reading and create an alert if thresholds exceeded\n"
    "  async evaluateReading(data) {\n"
    "    const { device_id, sound_db, vibration } = data;\n\n"
    "    const isAlert = sound_db     > SOUND_THRESHOLD ||\n"
    "                    vibration    > VIBRATION_THRESHOLD;\n\n"
    "    if (!isAlert) return null;\n\n"
    "    // Deduplication: skip if same device alerted recently\n"
    "    const duplicate = await alertModel.recentlyAlerted(\n"
    "      device_id, DEDUP_MINUTES\n"
    "    );\n\n"
    "    if (duplicate) {\n"
    + "      console.log(" + BT + "[AlertService] Duplicate suppressed for ${device_id}" + BT + ");\n"
    "      return null;\n"
    "    }\n\n"
    "    // Create the alert\n"
    "    const alert = await alertModel.create(data);\n"
    + "    console.log(" + BT + "[AlertService] ALERT created: ${device_id} | zone: ${data.zone} | sound: ${sound_db}dB" + BT + ");\n"
    "    return alert;\n"
    "  },\n\n"
    "};\n\n"
    "module.exports = alertService;\n"
))

# ─────────────────────────────────────────────────────────────
# 7. MQTT SERVICE — wired to DB
# ─────────────────────────────────────────────────────────────
print("\n[7/10] Wiring mqttService.js to DB...")

overwrite("backend/src/services/mqttService.js", (
    "const mqtt         = require('mqtt');\n"
    "const sensorModel  = require('../models/sensorModel');\n"
    "const alertService = require('./alertService');\n"
    "require('dotenv').config();\n\n"
    "const BROKER_URL = process.env.MQTT_BROKER || 'mqtt://localhost:1883';\n"
    "const TOPIC      = process.env.MQTT_TOPIC  || 'forest/sensor/data';\n\n"
    "function connectMQTT() {\n"
    "  const client = mqtt.connect(BROKER_URL);\n\n"
    "  client.on('connect', () => {\n"
    "    client.subscribe(TOPIC);\n"
    + "    console.log(" + BT + "[MQTT] Connected -> subscribed to: ${TOPIC}" + BT + ");\n"
    "  });\n\n"
    "  client.on('message', async (topic, message) => {\n"
    "    try {\n"
    "      const data = JSON.parse(message.toString());\n\n"
    "      // 1. Save every reading to sensor_readings table\n"
    "      const reading = await sensorModel.saveReading(data);\n"
    + "      console.log(" + BT + "[MQTT] Saved reading: ${data.device_id} | ${data.zone} | sound: ${data.sound_db}dB" + BT + ");\n\n"
    "      // 2. Check thresholds and create alert if needed\n"
    "      await alertService.evaluateReading(data);\n\n"
    "    } catch (err) {\n"
    + "      console.error(" + BT + "[MQTT] Error processing message: ${err.message}" + BT + ");\n"
    "    }\n"
    "  });\n\n"
    "  client.on('error', (err) => {\n"
    + "    console.error(" + BT + "[MQTT] Connection error: ${err.message}" + BT + ");\n"
    "  });\n\n"
    "  client.on('reconnect', () => {\n"
    "    console.log('[MQTT] Reconnecting...');\n"
    "  });\n"
    "}\n\n"
    "module.exports = { connectMQTT };\n"
))

# ─────────────────────────────────────────────────────────────
# 8. ROUTES — wired to models
# ─────────────────────────────────────────────────────────────
print("\n[8/10] Wiring routes to models...")

overwrite("backend/src/routes/sensors.js", (
    "const express     = require('express');\n"
    "const router      = express.Router();\n"
    "const sensorModel = require('../models/sensorModel');\n\n"
    "// GET /api/sensors — all readings (newest first, limit 100)\n"
    "router.get('/', async (req, res) => {\n"
    "  try {\n"
    "    const rows = await sensorModel.getAll();\n"
    "    res.json(rows);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/sensors/live — latest reading per device\n"
    "router.get('/live', async (req, res) => {\n"
    "  try {\n"
    "    const rows = await sensorModel.getLive();\n"
    "    res.json(rows);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/sensors/:device_id — readings for a specific device\n"
    "router.get('/:device_id', async (req, res) => {\n"
    "  try {\n"
    "    const rows = await sensorModel.getByDevice(req.params.device_id);\n"
    "    res.json(rows);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// POST /api/sensors — manual sensor data post (testing + fallback)\n"
    "router.post('/', async (req, res) => {\n"
    "  const { device_id } = req.body;\n"
    "  if (!device_id) {\n"
    "    return res.status(400).json({ error: 'device_id is required' });\n"
    "  }\n"
    "  try {\n"
    "    const reading = await sensorModel.saveReading(req.body);\n"
    "    res.status(201).json({ message: 'reading saved', data: reading });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "module.exports = router;\n"
))

overwrite("backend/src/routes/alerts.js", (
    "const express    = require('express');\n"
    "const router     = express.Router();\n"
    "const alertModel = require('../models/alertModel');\n\n"
    "// GET /api/alerts — all alerts newest first\n"
    "router.get('/', async (req, res) => {\n"
    "  try {\n"
    "    const alerts = await alertModel.getAll();\n"
    "    res.json(alerts);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/alerts/count — unresolved alert count (for navbar badge)\n"
    "router.get('/count', async (req, res) => {\n"
    "  try {\n"
    "    const count = await alertModel.countUnresolved();\n"
    "    res.json({ count });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/alerts/unresolved — only unresolved alerts\n"
    "router.get('/unresolved', async (req, res) => {\n"
    "  try {\n"
    "    const alerts = await alertModel.getUnresolved();\n"
    "    res.json(alerts);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/alerts/:id — single alert\n"
    "router.get('/:id', async (req, res) => {\n"
    "  try {\n"
    "    const alert = await alertModel.getById(req.params.id);\n"
    "    if (!alert) return res.status(404).json({ error: 'Alert not found' });\n"
    "    res.json(alert);\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// PATCH /api/alerts/:id/resolve — mark alert as resolved\n"
    "router.patch('/:id/resolve', async (req, res) => {\n"
    "  try {\n"
    "    const alert = await alertModel.resolve(req.params.id);\n"
    "    if (!alert) return res.status(404).json({ error: 'Alert not found' });\n"
    "    res.json({ message: 'Alert resolved', alert });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "module.exports = router;\n"
))

overwrite("backend/src/routes/auth.js", (
    "const express   = require('express');\n"
    "const router    = express.Router();\n"
    "const supabase  = require('../config/supabase');\n"
    "const userModel = require('../models/userModel');\n\n"
    "// POST /api/auth/login\n"
    "router.post('/login', async (req, res) => {\n"
    "  const { email, password } = req.body;\n"
    "  if (!email || !password) {\n"
    "    return res.status(400).json({ error: 'email and password are required' });\n"
    "  }\n"
    "  try {\n"
    "    const { data, error } = await supabase.auth.signInWithPassword({\n"
    "      email, password\n"
    "    });\n"
    "    if (error) return res.status(401).json({ error: error.message });\n\n"
    "    // Sync user profile to our users table\n"
    "    const profile = await userModel.create({\n"
    "      name  : data.user.user_metadata?.name || email.split('@')[0],\n"
    "      email : data.user.email,\n"
    "      role  : data.user.user_metadata?.role || 'ranger',\n"
    "    });\n\n"
    "    res.json({\n"
    "      token   : data.session.access_token,\n"
    "      expires : data.session.expires_at,\n"
    "      user    : {\n"
    "        id    : data.user.id,\n"
    "        email : data.user.email,\n"
    "        role  : profile.role,\n"
    "        name  : profile.name,\n"
    "      }\n"
    "    });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// POST /api/auth/logout\n"
    "router.post('/logout', async (req, res) => {\n"
    "  try {\n"
    "    await supabase.auth.signOut();\n"
    "    res.json({ message: 'Logged out successfully' });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "// GET /api/auth/me — return current user from token\n"
    "router.get('/me', async (req, res) => {\n"
    "  const authHeader = req.headers.authorization;\n"
    "  if (!authHeader || !authHeader.startsWith('Bearer ')) {\n"
    "    return res.status(401).json({ error: 'No token provided' });\n"
    "  }\n"
    "  const token = authHeader.split(' ')[1];\n"
    "  try {\n"
    "    const { data, error } = await supabase.auth.getUser(token);\n"
    "    if (error) return res.status(401).json({ error: error.message });\n"
    "    const profile = await userModel.getByEmail(data.user.email);\n"
    "    res.json({ user: { ...data.user, profile } });\n"
    "  } catch (err) {\n"
    "    res.status(500).json({ error: err.message });\n"
    "  }\n"
    "});\n\n"
    "module.exports = router;\n"
))

# ─────────────────────────────────────────────────────────────
# 9. ERROR HANDLER MIDDLEWARE
# ─────────────────────────────────────────────────────────────
print("\n[9/10] Implementing errorHandler + simulator upgrade...")

overwrite("backend/src/middleware/errorHandler.js", (
    "// Global Express error handler\n"
    "// Must be registered LAST in index.js with app.use(errorHandler)\n\n"
    "function errorHandler(err, req, res, next) {\n"
    "  const status = err.status || err.statusCode || 500;\n"
    "  const message = err.message || 'Internal server error';\n\n"
    + "  console.error(" + BT + "[Error] ${req.method} ${req.path} -> ${status}: ${message}" + BT + ");\n\n"
    "  res.status(status).json({\n"
    "    error     : message,\n"
    "    path      : req.path,\n"
    "    timestamp : new Date().toISOString(),\n"
    "  });\n"
    "}\n\n"
    "module.exports = errorHandler;\n"
))

# Update index.js to use errorHandler
overwrite("backend/src/index.js", (
    "const express      = require('express');\n"
    "const cors         = require('cors');\n"
    "const dotenv       = require('dotenv');\n"
    "const { connectMQTT } = require('./services/mqttService');\n"
    "const errorHandler = require('./middleware/errorHandler');\n\n"
    "dotenv.config();\n\n"
    "const app  = express();\n"
    "const PORT = process.env.PORT || 5000;\n\n"
    "app.use(cors());\n"
    "app.use(express.json());\n\n"
    "// Routes\n"
    "app.use('/api/alerts',  require('./routes/alerts'));\n"
    "app.use('/api/sensors', require('./routes/sensors'));\n"
    "app.use('/api/auth',    require('./routes/auth'));\n\n"
    "// Health check\n"
    "app.get('/api/health', (req, res) => {\n"
    "  res.json({ status: 'ok', timestamp: new Date().toISOString() });\n"
    "});\n\n"
    "// Global error handler (must be last)\n"
    "app.use(errorHandler);\n\n"
    "// Only start server + MQTT when not in test mode\n"
    "let server;\n"
    "if (process.env.NODE_ENV !== 'test') {\n"
    "  connectMQTT();\n"
    "  server = app.listen(PORT, () => {\n"
    + "    console.log(" + BT + "SmartForest backend running on http://localhost:${PORT}" + BT + ");\n"
    "  });\n"
    "}\n\n"
    "module.exports = { app, server };\n"
))

# ─────────────────────────────────────────────────────────────
# 10. SIMULATOR UPGRADE
# ─────────────────────────────────────────────────────────────

overwrite("simulator/mqtt_simulator.py", (
    "#!/usr/bin/env python3\n"
    "#\n"
    "# SmartForest MQTT IoT Simulator\n"
    "# Publishes fake sensor readings to test the full pipeline:\n"
    "#   Simulator -> MQTT Broker -> Backend -> Supabase DB\n"
    "#\n"
    "# Usage:\n"
    "#   source venv/bin/activate\n"
    "#   python mqtt_simulator.py\n"
    "#\n"
    "# Env vars (optional overrides):\n"
    "#   MQTT_BROKER_HOST  default: localhost\n"
    "#   MQTT_BROKER_PORT  default: 1883\n"
    "#   MQTT_TOPIC        default: forest/sensor/data\n"
    "#   SEND_INTERVAL     default: 5 (seconds between readings)\n"
    "#   SPIKE_CHANCE      default: 0.20 (20% chance of alert-level reading)\n\n"
    "import paho.mqtt.client as mqtt\n"
    "import json, random, time, os, sys\n"
    "from datetime import datetime, timezone\n\n"
    "BROKER   = os.getenv('MQTT_BROKER_HOST', 'localhost')\n"
    "PORT     = int(os.getenv('MQTT_BROKER_PORT', 1883))\n"
    "TOPIC    = os.getenv('MQTT_TOPIC', 'forest/sensor/data')\n"
    "INTERVAL = float(os.getenv('SEND_INTERVAL', 5))\n"
    "SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE', 0.20))\n\n"
    "ZONES = [\n"
    "    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},\n"
    "    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},\n"
    "    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},\n"
    "]\n\n"
    "# ── MQTT callbacks ──────────────────────────────────────\n"
    "def on_connect(client, userdata, flags, reason_code, properties):\n"
    "    if reason_code == 0:\n"
    "        print(f'[MQTT] Connected to broker at {BROKER}:{PORT}')\n"
    "    else:\n"
    "        print(f'[MQTT] Connection failed, reason code: {reason_code}')\n"
    "        sys.exit(1)\n\n"
    "def on_disconnect(client, userdata, flags, reason_code, properties):\n"
    "    if reason_code != 0:\n"
    "        print(f'[MQTT] Unexpected disconnect ({reason_code}) - will retry...')\n\n"
    "def on_publish(client, userdata, mid, reason_code, properties):\n"
    "    pass  # successful publish confirmed\n\n"
    "# ── Setup client ────────────────────────────────────────\n"
    "client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)\n"
    "client.on_connect    = on_connect\n"
    "client.on_disconnect = on_disconnect\n"
    "client.on_publish    = on_publish\n\n"
    "print(f'[SIM] Connecting to mqtt://{BROKER}:{PORT} ...')\n"
    "try:\n"
    "    client.connect(BROKER, PORT, keepalive=60)\n"
    "except Exception as e:\n"
    "    print(f'[SIM] ERROR: Cannot connect to broker -> {e}')\n"
    "    print('[SIM] Make sure Mosquitto is running:')\n"
    "    print('      sudo apt install mosquitto -y')\n"
    "    print('      mosquitto -c mosquitto.conf')\n"
    "    sys.exit(1)\n\n"
    "client.loop_start()  # non-blocking loop for reconnects\n"
    "time.sleep(1)        # wait for on_connect to fire\n\n"
    "print(f'[SIM] Publishing to topic: {TOPIC}')\n"
    "print(f'[SIM] Interval: {INTERVAL}s | Spike chance: {int(SPIKE_CHANCE*100)}%')\n"
    "print(f'[SIM] Press Ctrl+C to stop\\n')\n\n"
    "reading_count = 0\n"
    "alert_count   = 0\n\n"
    "try:\n"
    "    while True:\n"
    "        zone  = random.choice(ZONES)\n"
    "        spike = random.random() < SPIKE_CHANCE\n\n"
    "        payload = {\n"
    "            'device_id' : f\"SENSOR-{random.randint(1, 5):03d}\",\n"
    "            'timestamp' : datetime.now(timezone.utc).isoformat(),\n"
    "            'zone'      : zone['zone'],\n"
    "            'latitude'  : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),\n"
    "            'longitude' : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),\n"
    "            'sound_db'  : round(random.uniform(82, 98) if spike\n"
    "                                else random.uniform(20, 60), 2),\n"
    "            'vibration' : round(random.uniform(7.5, 10) if spike\n"
    "                                else random.uniform(0, 5), 2),\n"
    "        }\n\n"
    "        result = client.publish(TOPIC, json.dumps(payload))\n"
    "        reading_count += 1\n"
    "        if spike:\n"
    "            alert_count += 1\n\n"
    "        ts  = datetime.now().strftime('%H:%M:%S')\n"
    "        tag = '[ALERT]' if spike else '[  ok ]'\n"
    "        print(\n"
    "            f\"{ts} {tag} \"\n"
    "            f\"{payload['device_id']} | \"\n"
    "            f\"{payload['zone']} | \"\n"
    "            f\"Sound: {payload['sound_db']} dB | \"\n"
    "            f\"Vib: {payload['vibration']} | \"\n"
    "            f\"readings: {reading_count} alerts: {alert_count}\"\n"
    "        )\n\n"
    "        time.sleep(INTERVAL)\n\n"
    "except KeyboardInterrupt:\n"
    "    print(f'\\n[SIM] Stopped. Total readings: {reading_count}, alerts: {alert_count}')\n"
    "    client.loop_stop()\n"
    "    client.disconnect()\n"
))

# ─────────────────────────────────────────────────────────────
# DOCKER COMPOSE — remove frontend service (uses Vercel instead)
# ─────────────────────────────────────────────────────────────
overwrite("docker-compose.yml", (
    "version: '3.8'\n\n"
    "# Render.com cloud deployment only.\n"
    "# Frontend is on Vercel (no Docker needed there).\n"
    "# Local dev: run Node and Mosquitto directly without Docker.\n\n"
    "services:\n\n"
    "  backend:\n"
    "    build: ./backend\n"
    "    ports:\n"
    "      - \"5000:5000\"\n"
    "    env_file: ./backend/.env\n"
    "    depends_on:\n"
    "      - mqtt-broker\n"
    "    restart: unless-stopped\n\n"
    "  mqtt-broker:\n"
    "    image: eclipse-mosquitto:2\n"
    "    ports:\n"
    "      - \"1883:1883\"\n"
    "      - \"9001:9001\"\n"
    "    volumes:\n"
    "      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf\n"
    "    restart: unless-stopped\n\n"
    "  simulator:\n"
    "    build: ./simulator\n"
    "    environment:\n"
    "      - MQTT_BROKER_HOST=mqtt-broker\n"
    "      - MQTT_BROKER_PORT=1883\n"
    "      - MQTT_TOPIC=forest/sensor/data\n"
    "      - SEND_INTERVAL=5\n"
    "      - SPIKE_CHANCE=0.20\n"
    "    depends_on:\n"
    "      - mqtt-broker\n"
    "    restart: unless-stopped\n"
))

print("\n[10/10] Done!\n")
print("=" * 60)
print("  patch_sprint1.py completed")
print("=" * 60)
print("""
NEXT STEPS:
-----------
1. Run migrations in Supabase SQL Editor (in this order):
     database/migrations/001_create_users.sql
     database/migrations/002_create_sensor_readings.sql
     database/migrations/003_create_alerts.sql

2. Start MQTT broker:
     sudo apt install mosquitto -y
     mosquitto -c mosquitto.conf

3. Start backend:
     cd backend && npm run dev

4. Start simulator (new terminal):
     cd simulator
     source venv/bin/activate
     python mqtt_simulator.py

5. Verify data flowing:
     curl http://localhost:5000/api/health
     curl http://localhost:5000/api/sensors
     curl http://localhost:5000/api/alerts

6. Check Supabase dashboard -> Table Editor
     sensor_readings table should be filling up
     alerts table should show entries where sound_db > 80

7. Run tests:
     cd backend && npm test
""")
