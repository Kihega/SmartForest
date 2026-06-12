#!/usr/bin/env python3
"""
patch.py — SmartForest Project Master Setup Patch
Run from project root: python3 patch.py
"""

import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def mkfile(path, content=""):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if os.path.exists(full):
        print("  [SKIP]   " + path)
        return
    with open(full, "w") as f:
        f.write(content)
    print("  [CREATE] " + path)

def mkdir(path):
    os.makedirs(os.path.join(ROOT, path), exist_ok=True)

def overwrite(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("  [UPDATE] " + path)

# ─────────────────────────────────────────────────────────────
# All file contents defined as plain strings (no backtick JS)
# JS template literals written as raw strings to avoid escape issues
# ─────────────────────────────────────────────────────────────

GITIGNORE = (
    "# Dependencies\n"
    "node_modules/\n"
    "venv/\n\n"
    "# Environment variables\n"
    ".env\n"
    ".env.local\n"
    ".env.production\n"
    ".env.*.local\n\n"
    "# Build outputs\n"
    "dist/\n"
    "build/\n"
    ".vercel/\n\n"
    "# Python\n"
    "__pycache__/\n"
    "*.pyc\n"
    "*.pyo\n\n"
    "# Logs\n"
    "*.log\n"
    "npm-debug.log*\n\n"
    "# OS files\n"
    ".DS_Store\n"
    "Thumbs.db\n\n"
    "# Coverage\n"
    "coverage/\n\n"
    "# Editor\n"
    ".vscode/\n"
    ".idea/\n"
)

README = (
    "# SmartForest — Illegal Logging Detection System\n\n"
    "Real-time monitoring system for detecting illegal logging in Kibiti, Tanzania.\n\n"
    "## Stack\n"
    "- **Backend**: Node.js + Express.js (local or Render.com)\n"
    "- **Frontend**: React.js / Vite (local or Vercel)\n"
    "- **Database**: PostgreSQL via Supabase\n"
    "- **IoT Simulation**: MQTT (Mosquitto broker)\n\n"
    "## Quick Start\n\n"
    "### 1. MQTT Broker (local)\n"
    "```bash\n"
    "sudo apt install mosquitto -y\n"
    "mosquitto -c mosquitto.conf\n"
    "```\n\n"
    "### 2. Backend\n"
    "```bash\n"
    "cd backend && npm install\n"
    "cp .env.example .env   # fill in Supabase credentials\n"
    "npm run dev\n"
    "```\n\n"
    "### 3. Frontend\n"
    "```bash\n"
    "cd frontend && npm install\n"
    "cp .env.example .env\n"
    "npm run dev\n"
    "```\n\n"
    "### 4. Simulator\n"
    "```bash\n"
    "cd simulator\n"
    "python3 -m venv venv && source venv/bin/activate\n"
    "pip install -r requirements.txt\n"
    "python mqtt_simulator.py\n"
    "```\n\n"
    "## Branching\n"
    "- `develop` — daily work (local)\n"
    "- `main` — production (auto-merged after CI passes)\n"
)

DOCKER_COMPOSE = (
    "version: '3.8'\n\n"
    "# Used for Render.com cloud deployment only.\n"
    "# Local dev runs Node and Mosquitto directly (no Docker needed).\n\n"
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
    "    depends_on:\n"
    "      - mqtt-broker\n"
    "    restart: unless-stopped\n"
)

MOSQUITTO_CONF = (
    "listener 1883\n"
    "allow_anonymous true\n\n"
    "# WebSocket listener (for browser MQTT clients)\n"
    "listener 9001\n"
    "protocol websockets\n"
    "allow_anonymous true\n"
)

CI_YML = (
    "name: CI - Test, Build & Auto-Merge to Main\n\n"
    "on:\n"
    "  push:\n"
    "    branches: [develop]\n"
    "  pull_request:\n"
    "    branches: [main]\n\n"
    "jobs:\n\n"
    "  test-backend:\n"
    "    name: Backend Tests\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Node.js\n"
    "        uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '20'\n"
    "          cache: 'npm'\n"
    "          cache-dependency-path: backend/package-lock.json\n"
    "      - name: Install dependencies\n"
    "        working-directory: ./backend\n"
    "        run: npm ci\n"
    "      - name: Run tests\n"
    "        working-directory: ./backend\n"
    "        run: npm test\n\n"
    "  test-frontend:\n"
    "    name: Frontend Lint & Build\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Node.js\n"
    "        uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '20'\n"
    "          cache: 'npm'\n"
    "          cache-dependency-path: frontend/package-lock.json\n"
    "      - name: Install dependencies\n"
    "        working-directory: ./frontend\n"
    "        run: npm ci\n"
    "      - name: Lint\n"
    "        working-directory: ./frontend\n"
    "        run: npm run lint\n"
    "      - name: Build\n"
    "        working-directory: ./frontend\n"
    "        run: npm run build\n"
    "        env:\n"
    "          VITE_API_URL_CLOUD: ${{ secrets.VITE_API_URL_CLOUD }}\n"
    "          VITE_API_URL_LOCAL: http://localhost:5000/api\n\n"
    "  test-simulator:\n"
    "    name: Simulator Tests\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Python\n"
    "        uses: actions/setup-python@v5\n"
    "        with:\n"
    "          python-version: '3.11'\n"
    "      - name: Install dependencies\n"
    "        run: pip install -r simulator/requirements.txt\n"
    "      - name: Run tests\n"
    "        run: pytest simulator/tests/ -v\n\n"
    "  docker-build:\n"
    "    name: Docker Build Check\n"
    "    runs-on: ubuntu-latest\n"
    "    needs: [test-backend, test-frontend]\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Build backend Docker image\n"
    "        run: docker build ./backend -t smartforest-backend\n\n"
    "  auto-merge-to-main:\n"
    "    name: Auto-merge to Main\n"
    "    runs-on: ubuntu-latest\n"
    "    needs: [test-backend, test-frontend, test-simulator, docker-build]\n"
    "    if: github.ref == 'refs/heads/develop' && github.event_name == 'push'\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "        with:\n"
    "          fetch-depth: 0\n"
    "          token: ${{ secrets.GITHUB_TOKEN }}\n"
    "      - name: Configure Git\n"
    "        run: |\n"
    "          git config user.name \"github-actions[bot]\"\n"
    "          git config user.email \"github-actions[bot]@users.noreply.github.com\"\n"
    "      - name: Merge develop into main\n"
    "        run: |\n"
    "          git checkout main\n"
    "          git merge develop --no-ff -m \"ci: auto-merge develop into main [skip ci]\"\n"
    "          git push origin main\n"
)

BACKEND_ENV_EXAMPLE = (
    "# Copy this to .env and fill in your values\n"
    "PORT=5000\n"
    "NODE_ENV=development\n\n"
    "# Supabase PostgreSQL (direct connection string)\n"
    "DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres\n\n"
    "# Supabase API (Auth + JWT session management)\n"
    "SUPABASE_URL=https://[REF].supabase.co\n"
    "SUPABASE_ANON_KEY=your-anon-key-here\n"
    "SUPABASE_SERVICE_KEY=your-service-role-key-here\n\n"
    "# JWT\n"
    "JWT_SECRET=your-super-secret-jwt-key\n\n"
    "# MQTT Broker\n"
    "MQTT_BROKER=mqtt://localhost:1883\n"
    "MQTT_TOPIC=forest/sensor/data\n\n"
    "# Alert thresholds\n"
    "SOUND_THRESHOLD_DB=80\n"
    "VIBRATION_THRESHOLD=7\n"
)

BACKEND_PACKAGE_JSON = (
    '{\n'
    '  "name": "backend",\n'
    '  "version": "1.0.0",\n'
    '  "description": "SmartForest illegal logging detection backend",\n'
    '  "main": "src/index.js",\n'
    '  "type": "commonjs",\n'
    '  "scripts": {\n'
    '    "start": "node src/index.js",\n'
    '    "dev": "nodemon src/index.js",\n'
    '    "test": "jest --forceExit"\n'
    '  },\n'
    '  "dependencies": {\n'
    '    "@supabase/supabase-js": "^2.49.0",\n'
    '    "cors": "^2.8.6",\n'
    '    "dotenv": "^17.4.2",\n'
    '    "express": "^5.2.1",\n'
    '    "mqtt": "^5.15.1",\n'
    '    "pg": "^8.21.0"\n'
    '  },\n'
    '  "devDependencies": {\n'
    '    "jest": "^30.4.2",\n'
    '    "nodemon": "^3.1.14",\n'
    '    "supertest": "^7.2.2"\n'
    '  }\n'
    '}\n'
)

# JS files: use single-quoted strings, write backticks as literal chars via chr(96)
BT = chr(96)  # backtick character

BACKEND_INDEX = (
    "const express  = require('express');\n"
    "const cors     = require('cors');\n"
    "const dotenv   = require('dotenv');\n"
    "const { connectMQTT } = require('./services/mqttService');\n\n"
    "dotenv.config();\n\n"
    "const app  = express();\n"
    "const PORT = process.env.PORT || 5000;\n\n"
    "app.use(cors());\n"
    "app.use(express.json());\n\n"
    "// Routes\n"
    "app.use('/api/alerts',  require('./routes/alerts'));\n"
    "app.use('/api/sensors', require('./routes/sensors'));\n"
    "app.use('/api/auth',    require('./routes/auth'));\n\n"
    "// Health check — used by frontend to detect if backend is live\n"
    "app.get('/api/health', (req, res) => {\n"
    "  res.json({ status: 'ok', timestamp: new Date().toISOString() });\n"
    "});\n\n"
    "// Start MQTT subscriber\n"
    "connectMQTT();\n\n"
    "app.listen(PORT, () => {\n"
    + "  console.log(" + BT + "SmartForest backend running on http://localhost:${PORT}" + BT + ");\n"
    "});\n\n"
    "module.exports = app;\n"
)

BACKEND_DB = (
    "const { Pool } = require('pg');\n"
    "require('dotenv').config();\n\n"
    "const pool = new Pool({\n"
    "  connectionString: process.env.DATABASE_URL,\n"
    "  ssl: { rejectUnauthorized: false },\n"
    "});\n\n"
    "pool.on('connect', () => {\n"
    "  console.log('Connected to Supabase PostgreSQL');\n"
    "});\n\n"
    "module.exports = pool;\n"
)

BACKEND_SUPABASE = (
    "const { createClient } = require('@supabase/supabase-js');\n"
    "require('dotenv').config();\n\n"
    "const supabase = createClient(\n"
    "  process.env.SUPABASE_URL,\n"
    "  process.env.SUPABASE_SERVICE_KEY\n"
    ");\n\n"
    "module.exports = supabase;\n"
)

BACKEND_MQTT = (
    "const mqtt = require('mqtt');\n"
    "require('dotenv').config();\n\n"
    "const BROKER_URL          = process.env.MQTT_BROKER || 'mqtt://localhost:1883';\n"
    "const TOPIC               = process.env.MQTT_TOPIC  || 'forest/sensor/data';\n"
    "const SOUND_THRESHOLD     = parseFloat(process.env.SOUND_THRESHOLD_DB || 80);\n"
    "const VIBRATION_THRESHOLD = parseFloat(process.env.VIBRATION_THRESHOLD || 7);\n\n"
    "function connectMQTT() {\n"
    "  const client = mqtt.connect(BROKER_URL);\n\n"
    "  client.on('connect', () => {\n"
    "    client.subscribe(TOPIC);\n"
    + "    console.log(" + BT + "MQTT connected — subscribed to: ${TOPIC}" + BT + ");\n"
    "  });\n\n"
    "  client.on('message', async (topic, message) => {\n"
    "    try {\n"
    "      const data    = JSON.parse(message.toString());\n"
    "      const isAlert = data.sound_db > SOUND_THRESHOLD ||\n"
    "                      data.vibration > VIBRATION_THRESHOLD;\n"
    "      // TODO: call sensorModel.saveReading() and alertService.handleAlert()\n"
    + "      console.log(" + BT + "Sensor: ${data.device_id} | Sound: ${data.sound_db}dB | Alert: ${isAlert}" + BT + ");\n"
    "    } catch (err) {\n"
    "      console.error('MQTT message error:', err.message);\n"
    "    }\n"
    "  });\n\n"
    "  client.on('error', (err) => {\n"
    "    console.error('MQTT connection error:', err.message);\n"
    "  });\n"
    "}\n\n"
    "module.exports = { connectMQTT };\n"
)

BACKEND_DOCKERFILE = (
    "FROM node:20-alpine\n"
    "WORKDIR /app\n"
    "COPY package*.json ./\n"
    "RUN npm ci --only=production\n"
    "COPY . .\n"
    "EXPOSE 5000\n"
    "CMD [\"node\", \"src/index.js\"]\n"
)

FRONTEND_ENV_EXAMPLE = (
    "# Primary: Render.com cloud backend (checked first)\n"
    "VITE_API_URL_CLOUD=https://your-app.onrender.com/api\n\n"
    "# Fallback: local backend\n"
    "VITE_API_URL_LOCAL=http://localhost:5000/api\n"
)

VERCEL_JSON = (
    '{\n'
    '  "rewrites": [\n'
    '    { "source": "/(.*)", "destination": "/index.html" }\n'
    '  ]\n'
    '}\n'
)

FRONTEND_API = (
    "/**\n"
    " * api.js — Smart backend resolver\n"
    " *\n"
    " * Priority:\n"
    " *  1. Try VITE_API_URL_CLOUD (Render.com) — 4s timeout\n"
    " *  2. Try VITE_API_URL_LOCAL (localhost)  — 2s timeout\n"
    " *  3. Both fail -> throw 'NO_BACKEND' error\n"
    " *\n"
    " * BackendStatus.jsx catches NO_BACKEND and shows a visible banner.\n"
    " */\n"
    "import axios from 'axios';\n\n"
    "const CLOUD_URL = import.meta.env.VITE_API_URL_CLOUD;\n"
    "const LOCAL_URL = import.meta.env.VITE_API_URL_LOCAL || 'http://localhost:5000/api';\n\n"
    "let resolvedBaseURL = null;\n\n"
    "export async function resolveBackend() {\n"
    "  if (resolvedBaseURL) return resolvedBaseURL;\n\n"
    "  // 1. Try cloud (Render.com)\n"
    "  if (CLOUD_URL) {\n"
    "    try {\n"
    "      await axios.get(CLOUD_URL + '/health', { timeout: 4000 });\n"
    "      resolvedBaseURL = CLOUD_URL;\n"
    "      console.log('Backend: cloud (Render)');\n"
    "      return resolvedBaseURL;\n"
    "    } catch {\n"
    "      console.warn('Cloud backend unreachable, trying local...');\n"
    "    }\n"
    "  }\n\n"
    "  // 2. Try local\n"
    "  try {\n"
    "    await axios.get(LOCAL_URL + '/health', { timeout: 2000 });\n"
    "    resolvedBaseURL = LOCAL_URL;\n"
    "    console.log('Backend: local');\n"
    "    return resolvedBaseURL;\n"
    "  } catch {\n"
    "    throw new Error('NO_BACKEND');\n"
    "  }\n"
    "}\n\n"
    "export async function getAPI() {\n"
    "  const baseURL = await resolveBackend();\n"
    "  return axios.create({ baseURL });\n"
    "}\n\n"
    "export const getAlerts  = async () => (await getAPI()).get('/alerts');\n"
    "export const getSensors = async () => (await getAPI()).get('/sensors');\n"
    "export const getHealth  = async () => (await getAPI()).get('/health');\n"
)

FRONTEND_DOCKERFILE = (
    "FROM node:20-alpine AS builder\n"
    "WORKDIR /app\n"
    "COPY package*.json ./\n"
    "RUN npm ci\n"
    "COPY . .\n"
    "RUN npm run build\n\n"
    "FROM nginx:alpine\n"
    "COPY --from=builder /app/dist /usr/share/nginx/html\n"
    "EXPOSE 80\n"
    'CMD ["nginx", "-g", "daemon off;"]\n'
)

SIMULATOR_SCRIPT = (
    "# SmartForest MQTT IoT Simulator\n"
    "# Simulates chainsaw-sound and vibration sensors in Kibiti forest zones.\n"
    "#\n"
    "# Run locally:  source venv/bin/activate && python mqtt_simulator.py\n"
    "# Host on cloud: Railway.app or Render.com (see project-setup-summary.txt)\n\n"
    "import paho.mqtt.client as mqtt\n"
    "import json, random, time, os\n"
    "from datetime import datetime, timezone\n\n"
    "BROKER = os.getenv('MQTT_BROKER_HOST', 'localhost')\n"
    "PORT   = int(os.getenv('MQTT_BROKER_PORT', 1883))\n"
    "TOPIC  = os.getenv('MQTT_TOPIC', 'forest/sensor/data')\n\n"
    "ZONES = [\n"
    "    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},\n"
    "    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},\n"
    "    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},\n"
    "]\n\n"
    "client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)\n"
    "client.connect(BROKER, PORT)\n"
    "print(f'Simulator started -> mqtt://{BROKER}:{PORT}/{TOPIC}')\n\n"
    "while True:\n"
    "    zone  = random.choice(ZONES)\n"
    "    spike = random.random() < 0.20   # 20% chance = suspicious activity\n\n"
    "    payload = {\n"
    "        'device_id' : f\"SENSOR-{random.randint(1, 5):03d}\",\n"
    "        'timestamp' : datetime.now(timezone.utc).isoformat(),\n"
    "        'zone'      : zone['zone'],\n"
    "        'latitude'  : zone['lat'] + random.uniform(-0.01, 0.01),\n"
    "        'longitude' : zone['lng'] + random.uniform(-0.01, 0.01),\n"
    "        'sound_db'  : round(random.uniform(82, 98) if spike else random.uniform(20, 60), 2),\n"
    "        'vibration' : round(random.uniform(7.5, 10) if spike else random.uniform(0, 5), 2),\n"
    "    }\n\n"
    "    client.publish(TOPIC, json.dumps(payload))\n"
    "    tag = 'ALERT ' if spike else 'normal'\n"
    "    print(f\"[{tag}] {payload['zone']} | Sound: {payload['sound_db']} dB | Vib: {payload['vibration']}\")\n"
    "    time.sleep(5)\n"
)

SIMULATOR_REQUIREMENTS = (
    "paho-mqtt==2.1.0\n"
    "pytest==8.3.5\n"
)

SIMULATOR_TESTS = (
    '"""Unit tests for simulator payload structure."""\n\n\n'
    "def make_payload(spike=False):\n"
    "    from datetime import datetime, timezone\n"
    "    zone = {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95}\n"
    "    return {\n"
    "        'device_id' : 'SENSOR-001',\n"
    "        'timestamp' : datetime.now(timezone.utc).isoformat(),\n"
    "        'zone'      : zone['zone'],\n"
    "        'latitude'  : zone['lat'],\n"
    "        'longitude' : zone['lng'],\n"
    "        'sound_db'  : 90.0 if spike else 40.0,\n"
    "        'vibration' : 8.0  if spike else 2.0,\n"
    "    }\n\n\n"
    "def test_payload_has_required_fields():\n"
    "    p = make_payload()\n"
    "    required = ['device_id', 'timestamp', 'zone', 'latitude', 'longitude', 'sound_db', 'vibration']\n"
    "    for field in required:\n"
    "        assert field in p, f'Missing field: {field}'\n\n\n"
    "def test_spike_exceeds_threshold():\n"
    "    p = make_payload(spike=True)\n"
    "    assert p['sound_db'] > 80 or p['vibration'] > 7\n\n\n"
    "def test_normal_below_threshold():\n"
    "    p = make_payload(spike=False)\n"
    "    assert p['sound_db'] < 80 and p['vibration'] < 7\n\n\n"
    "def test_sound_db_is_float():\n"
    "    p = make_payload()\n"
    "    assert isinstance(p['sound_db'], float)\n"
)

SIMULATOR_DOCKERFILE = (
    "FROM python:3.11-slim\n"
    "WORKDIR /app\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY . .\n"
    'CMD ["python", "mqtt_simulator.py"]\n'
)

MIGRATION_001 = (
    "-- Run in Supabase SQL Editor (first)\n"
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
    "CREATE INDEX idx_sensor_readings_device ON sensor_readings(device_id);\n"
    "CREATE INDEX idx_sensor_readings_time   ON sensor_readings(recorded_at DESC);\n"
)

MIGRATION_002 = (
    "-- Run in Supabase SQL Editor (second, after users table)\n"
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
    "CREATE INDEX idx_alerts_status ON alerts(status);\n"
    "CREATE INDEX idx_alerts_time   ON alerts(created_at DESC);\n"
)

MIGRATION_003 = (
    "-- Run in Supabase SQL Editor (third)\n"
    "-- Auth/passwords are handled by Supabase Auth.\n"
    "-- This table stores profile/role data.\n"
    "CREATE TABLE IF NOT EXISTS users (\n"
    "  id         SERIAL PRIMARY KEY,\n"
    "  name       VARCHAR(100),\n"
    "  email      VARCHAR(100)  UNIQUE NOT NULL,\n"
    "  role       VARCHAR(20)   DEFAULT 'ranger',\n"
    "  created_at TIMESTAMPTZ   DEFAULT NOW()\n"
    ");\n"
)

SEED_SQL = (
    "-- Sample data for testing (run after migrations)\n"
    "INSERT INTO sensor_readings (device_id, zone, latitude, longitude, sound_db, vibration, is_alert)\n"
    "VALUES\n"
    "  ('SENSOR-001', 'Kibiti-North', -7.72,  38.95, 45.2, 2.1, FALSE),\n"
    "  ('SENSOR-002', 'Kibiti-South', -7.85,  38.88, 91.5, 8.3, TRUE),\n"
    "  ('SENSOR-003', 'Kibiti-East',  -7.78,  39.05, 33.0, 1.5, FALSE);\n\n"
    "INSERT INTO alerts (device_id, zone, latitude, longitude, sound_db, vibration, status)\n"
    "VALUES\n"
    "  ('SENSOR-002', 'Kibiti-South', -7.85, 38.88, 91.5, 8.3, 'unresolved');\n"
)

SETUP_SUMMARY = (
    "=====================================================================\n"
    "  SMARTFOREST - ILLEGAL LOGGING DETECTION SYSTEM\n"
    "  PROJECT SETUP SUMMARY (v3 - Updated)\n"
    "=====================================================================\n"
    "  Stack  : Express.js | React.js | PostgreSQL (Supabase) | MQTT\n"
    "  Region : Kibiti Forest, Tanzania\n"
    "  Updated: June 2026\n"
    "=====================================================================\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "1. TECH STACK OVERVIEW\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  Layer            | Technology              | Purpose\n"
    "  -----------------|-------------------------|---------------------------\n"
    "  Backend          | Node.js + Express.js    | REST API + MQTT subscriber\n"
    "  Frontend         | React.js (Vite)         | Live dashboard & alerts UI\n"
    "  Database         | PostgreSQL via Supabase | Data store + Auth/JWT cache\n"
    "  IoT Simulation   | MQTT (Mosquitto)        | Fake hardware sensor data\n"
    "  Local Dev        | Node only (no Docker)   | Kali Linux minimal machine\n"
    "  Backend Cloud    | Render.com (Docker)     | Cloud backend hosting\n"
    "  Frontend Cloud   | Vercel                  | Frontend hosting (free)\n"
    "  Version Control  | Git + GitHub            | Source control\n"
    "  CI/CD            | GitHub Actions          | Auto-test + auto-merge\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "2. TWO ENVIRONMENTS\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  A) LOCAL - Kali Linux / Nethunter on Termux\n"
    "     - No Docker required\n"
    "     - Backend  : plain Node  (npm run dev -> localhost:5000)\n"
    "     - Frontend : Vite dev    (npm run dev -> localhost:5173)\n"
    "     - MQTT     : Mosquitto via apt\n"
    "     - Simulator: Python in venv\n"
    "     - Database : Supabase cloud (no local DB needed)\n"
    "\n"
    "  B) CLOUD\n"
    "     - Backend  : Render.com (free tier, Docker container)\n"
    "     - Frontend : Vercel     (free tier, auto-deploy from GitHub)\n"
    "     - MQTT     : Mosquitto in Docker on Render\n"
    "     - Simulator: Railway.app (optional, see Section 8)\n"
    "     - Database : Same Supabase project\n"
    "\n"
    "  Local Mosquitto install:\n"
    "    sudo apt install mosquitto mosquitto-clients -y\n"
    "    mosquitto -c mosquitto.conf\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "3. PROJECT FOLDER STRUCTURE\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  SmartForest/\n"
    "  |\n"
    "  +-- patch.py                        Master setup/patch script\n"
    "  +-- docker-compose.yml              Render.com cloud deploy only\n"
    "  +-- mosquitto.conf                  MQTT broker config\n"
    "  +-- vercel.json                     Vercel SPA routing config\n"
    "  +-- README.md\n"
    "  +-- .gitignore\n"
    "  +-- project-setup-summary.txt\n"
    "  |\n"
    "  +-- backend/\n"
    "  |   +-- src/\n"
    "  |   |   +-- index.js               Entry + /api/health endpoint\n"
    "  |   |   +-- config/\n"
    "  |   |   |   +-- db.js              Supabase PostgreSQL pool\n"
    "  |   |   |   +-- supabase.js        Supabase client (Auth/JWT)\n"
    "  |   |   +-- routes/\n"
    "  |   |   |   +-- alerts.js          Alert CRUD\n"
    "  |   |   |   +-- sensors.js         Sensor data\n"
    "  |   |   |   +-- auth.js            Login / JWT verify\n"
    "  |   |   +-- services/\n"
    "  |   |   |   +-- mqttService.js     MQTT subscriber\n"
    "  |   |   |   +-- alertService.js    Alert logic\n"
    "  |   |   |   +-- notificationService.js  Email/SMS alerts\n"
    "  |   |   +-- models/\n"
    "  |   |   |   +-- sensorModel.js     sensor_readings queries\n"
    "  |   |   |   +-- alertModel.js      alerts queries\n"
    "  |   |   |   +-- userModel.js       users queries\n"
    "  |   |   +-- middleware/\n"
    "  |   |       +-- authMiddleware.js  JWT verification\n"
    "  |   |       +-- errorHandler.js    Global error handler\n"
    "  |   +-- tests/\n"
    "  |   |   +-- alerts.test.js\n"
    "  |   |   +-- sensors.test.js\n"
    "  |   |   +-- auth.test.js\n"
    "  |   +-- .env.example\n"
    "  |   +-- package.json\n"
    "  |   +-- Dockerfile\n"
    "  |\n"
    "  +-- frontend/\n"
    "  |   +-- src/\n"
    "  |   |   +-- App.jsx\n"
    "  |   |   +-- main.jsx\n"
    "  |   |   +-- services/\n"
    "  |   |   |   +-- api.js             Smart dual-backend resolver\n"
    "  |   |   +-- pages/\n"
    "  |   |   |   +-- Dashboard.jsx      Live monitoring page\n"
    "  |   |   |   +-- Login.jsx          Ranger login\n"
    "  |   |   |   +-- AlertDetail.jsx    Single alert view\n"
    "  |   |   +-- components/\n"
    "  |   |   |   +-- AlertsTable.jsx    Live alerts table\n"
    "  |   |   |   +-- ForestMap.jsx      Leaflet map + sensor pins\n"
    "  |   |   |   +-- SensorCard.jsx     Per-sensor status card\n"
    "  |   |   |   +-- Navbar.jsx         Top navigation\n"
    "  |   |   |   +-- BackendStatus.jsx  No-backend error banner\n"
    "  |   |   +-- context/\n"
    "  |   |   |   +-- AuthContext.jsx    JWT + user role state\n"
    "  |   |   |   +-- AlertContext.jsx   Live alerts global state\n"
    "  |   |   +-- hooks/\n"
    "  |   |       +-- useAlerts.js       Poll /api/alerts every 10s\n"
    "  |   |       +-- useSensors.js      Poll /api/sensors/live 5s\n"
    "  |   |       +-- useBackend.js      Resolve backend on mount\n"
    "  |   +-- public/\n"
    "  |   +-- .env.example\n"
    "  |   +-- vercel.json                Vercel SPA routing\n"
    "  |   +-- package.json\n"
    "  |   +-- Dockerfile                 For local Docker only\n"
    "  |\n"
    "  +-- simulator/\n"
    "  |   +-- mqtt_simulator.py\n"
    "  |   +-- requirements.txt\n"
    "  |   +-- Dockerfile\n"
    "  |   +-- tests/\n"
    "  |       +-- test_simulator.py\n"
    "  |\n"
    "  +-- database/\n"
    "  |   +-- migrations/\n"
    "  |   |   +-- 001_create_sensor_readings.sql\n"
    "  |   |   +-- 002_create_alerts.sql\n"
    "  |   |   +-- 003_create_users.sql\n"
    "  |   +-- seeds/\n"
    "  |       +-- dev_seed.sql\n"
    "  |\n"
    "  +-- .github/\n"
    "      +-- workflows/\n"
    "          +-- ci.yml\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "4. SUPABASE DATABASE SETUP\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  1. Create free project at https://supabase.com\n"
    "  2. Open SQL Editor, run in order:\n"
    "       database/migrations/001_create_sensor_readings.sql\n"
    "       database/migrations/002_create_alerts.sql\n"
    "       database/migrations/003_create_users.sql\n"
    "  3. Optional: run database/seeds/dev_seed.sql for test data\n"
    "  4. Copy credentials from Settings > API into backend/.env\n"
    "\n"
    "  Supabase provides:\n"
    "    - PostgreSQL database\n"
    "    - Auth server (JWT creation + in-memory session cache)\n"
    "    - Row-Level Security for per-user access\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "5. FRONTEND SMART BACKEND RESOLVER\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  On startup, src/services/api.js auto-detects backend:\n"
    "\n"
    "    Step 1 -> Try VITE_API_URL_CLOUD (Render.com), 4s timeout\n"
    "    Step 2 -> Try VITE_API_URL_LOCAL (localhost:5000), 2s timeout\n"
    "    Step 3 -> Both fail -> throw NO_BACKEND error\n"
    "\n"
    "  BackendStatus.jsx catches NO_BACKEND and shows an error banner.\n"
    "\n"
    "  Frontend .env:\n"
    "    VITE_API_URL_CLOUD=https://your-app.onrender.com/api\n"
    "    VITE_API_URL_LOCAL=http://localhost:5000/api\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "6. VERCEL FRONTEND DEPLOYMENT\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  Vercel is the recommended frontend host (free, fast, GitHub-linked).\n"
    "\n"
    "  SETUP:\n"
    "    1. Go to https://vercel.com -> New Project\n"
    "    2. Import your GitHub repo (SmartForest)\n"
    "    3. Set Root Directory = frontend\n"
    "    4. Framework Preset = Vite\n"
    "    5. Add environment variables:\n"
    "         VITE_API_URL_CLOUD  = https://your-app.onrender.com/api\n"
    "         VITE_API_URL_LOCAL  = http://localhost:5000/api\n"
    "    6. Deploy\n"
    "\n"
    "  AUTO-DEPLOY:\n"
    "    Vercel watches your GitHub main branch.\n"
    "    Every push to main -> Vercel rebuilds and redeploys frontend.\n"
    "    Since CI auto-merges develop->main, the full pipeline is:\n"
    "      git push develop -> CI tests -> merge to main -> Vercel deploys\n"
    "\n"
    "  vercel.json (in frontend folder):\n"
    "    Configures SPA routing so React Router works on direct URL loads.\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "7. GIT & GITHUB WORKFLOW\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  BRANCHES:\n"
    "    develop -> your daily local branch\n"
    "    main    -> production (GitHub), auto-merged after CI passes\n"
    "\n"
    "  INITIAL SETUP:\n"
    "    git init\n"
    "    git add .\n"
    "    git commit -m \"chore: initial project structure\"\n"
    "    git remote add origin https://github.com/YOUR/SmartForest.git\n"
    "    git branch -M develop\n"
    "    git push -u origin develop\n"
    "    git push origin develop:main   # create main on GitHub too\n"
    "\n"
    "  DAILY:\n"
    "    git add .\n"
    "    git commit -m \"feat: add sensor alert route\"\n"
    "    git push origin develop\n"
    "    -> GitHub Actions fires automatically\n"
    "    -> All tests pass -> develop auto-merged into main\n"
    "    -> Vercel sees main updated -> frontend redeployed\n"
    "\n"
    "  COMMIT FORMAT:\n"
    "    feat:  new feature\n"
    "    fix:   bug fix\n"
    "    docs:  documentation\n"
    "    test:  tests only\n"
    "    chore: config/setup\n"
    "    ci:    CI pipeline change\n"
    "\n"
    "  GitHub Secrets needed (Settings > Secrets > Actions):\n"
    "    VITE_API_URL_CLOUD  your Render backend URL\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "8. MQTT SIMULATOR - LOCAL vs CLOUD\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  LOCAL (recommended during development):\n"
    "    cd simulator\n"
    "    python3 -m venv venv\n"
    "    source venv/bin/activate\n"
    "    pip install -r requirements.txt\n"
    "    python mqtt_simulator.py\n"
    "\n"
    "  CLOUD HOSTING OPTIONS (when you want it always running):\n"
    "\n"
    "    Option A: Railway.app (easiest)\n"
    "      1. https://railway.app -> New Project -> GitHub repo\n"
    "      2. Root directory: /simulator\n"
    "      3. Railway auto-detects Dockerfile and deploys\n"
    "      4. Set env: MQTT_BROKER_HOST=your-hivemq-host\n"
    "\n"
    "    Option B: Render.com (Background Worker)\n"
    "      1. New -> Background Worker -> connect GitHub repo\n"
    "      2. Root: /simulator\n"
    "      3. Build: pip install -r requirements.txt\n"
    "      4. Start: python mqtt_simulator.py\n"
    "\n"
    "  IMPORTANT: Cloud simulator needs a cloud-accessible MQTT broker.\n"
    "  Use HiveMQ Cloud free tier: https://www.hivemq.com/mqtt-cloud-broker/\n"
    "  Both Render backend and Railway simulator connect to HiveMQ.\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "9. KEY API ENDPOINTS\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  Method  Endpoint                   Description\n"
    "  ------  -------------------------  --------------------------------\n"
    "  GET     /api/health                Is backend alive? (no auth)\n"
    "  POST    /api/auth/login            Ranger login -> JWT token\n"
    "  POST    /api/auth/logout           Invalidate session\n"
    "  GET     /api/alerts                All alerts (auth required)\n"
    "  GET     /api/alerts/:id            Single alert detail\n"
    "  PATCH   /api/alerts/:id/resolve    Mark alert as resolved\n"
    "  GET     /api/sensors               All sensor readings\n"
    "  GET     /api/sensors/live          Latest reading per device\n"
    "  POST    /api/sensors               Manual sensor post (testing)\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "10. QUICK START - LOCAL DEVELOPMENT\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  Terminal 1: MQTT Broker\n"
    "    sudo apt install mosquitto -y\n"
    "    mosquitto -c mosquitto.conf\n"
    "\n"
    "  Terminal 2: Backend\n"
    "    cd backend\n"
    "    cp .env.example .env   <- fill in Supabase creds\n"
    "    npm install\n"
    "    npm run dev            -> http://localhost:5000\n"
    "\n"
    "  Terminal 3: Frontend\n"
    "    cd frontend\n"
    "    cp .env.example .env\n"
    "    npm install\n"
    "    npm run dev            -> http://localhost:5173\n"
    "\n"
    "  Terminal 4: Simulator\n"
    "    cd simulator\n"
    "    source venv/bin/activate\n"
    "    python mqtt_simulator.py\n"
    "\n"
    "  Open http://localhost:5173 and watch live alerts appear!\n"
    "\n"
    "\n"
    "---------------------------------------------------------------------\n"
    "11. FULL DEPLOYMENT PIPELINE (end to end)\n"
    "---------------------------------------------------------------------\n"
    "\n"
    "  1. Write code locally on 'develop' branch\n"
    "  2. git push origin develop\n"
    "  3. GitHub Actions runs:\n"
    "       - Backend Jest tests\n"
    "       - Frontend lint + Vite build\n"
    "       - Simulator pytest tests\n"
    "       - Docker build check\n"
    "  4. ALL PASS -> develop auto-merged into main\n"
    "  5. Render.com detects main change -> redeploys backend\n"
    "  6. Vercel detects main change -> redeploys frontend\n"
    "  7. Production is live with new code\n"
    "\n"
    "=====================================================================\n"
    "  END OF SETUP SUMMARY\n"
    "  SmartForest - Protecting Kibiti Forest, Tanzania\n"
    "=====================================================================\n"
)

# ─────────────────────────────────────────────────────────────
# APPLY ALL FILES
# ─────────────────────────────────────────────────────────────

print("\n[1/8] Root-level files...")
overwrite(".gitignore",           GITIGNORE)
mkfile("README.md",               README)
mkfile("docker-compose.yml",      DOCKER_COMPOSE)
mkfile("mosquitto.conf",          MOSQUITTO_CONF)
mkfile("vercel.json",             VERCEL_JSON)

print("\n[2/8] GitHub Actions CI/CD...")
mkdir(".github/workflows")
overwrite(".github/workflows/ci.yml", CI_YML)

print("\n[3/8] Backend files...")
overwrite("backend/package.json",                     BACKEND_PACKAGE_JSON)
mkfile("backend/.env.example",                        BACKEND_ENV_EXAMPLE)
mkfile("backend/src/index.js",                        BACKEND_INDEX)
mkfile("backend/src/config/db.js",                    BACKEND_DB)
mkfile("backend/src/config/supabase.js",              BACKEND_SUPABASE)
mkfile("backend/src/routes/alerts.js",                "// TODO: alert CRUD routes\n")
mkfile("backend/src/routes/sensors.js",               "// TODO: sensor data routes\n")
mkfile("backend/src/routes/auth.js",                  "// TODO: login/logout/verify routes\n")
mkfile("backend/src/services/mqttService.js",         BACKEND_MQTT)
mkfile("backend/src/services/alertService.js",        "// TODO: alert creation and dispatch\n")
mkfile("backend/src/services/notificationService.js", "// TODO: email/SMS on alert trigger\n")
mkfile("backend/src/models/sensorModel.js",           "// TODO: sensor_readings DB queries\n")
mkfile("backend/src/models/alertModel.js",            "// TODO: alerts DB queries\n")
mkfile("backend/src/models/userModel.js",             "// TODO: users DB queries\n")
mkfile("backend/src/middleware/authMiddleware.js",     "// TODO: JWT verification middleware\n")
mkfile("backend/src/middleware/errorHandler.js",       "// TODO: global Express error handler\n")
mkfile("backend/tests/alerts.test.js",                "// TODO: alert endpoint tests\n")
mkfile("backend/tests/sensors.test.js",               "// TODO: sensor endpoint tests\n")
mkfile("backend/tests/auth.test.js",                  "// TODO: auth endpoint tests\n")
mkfile("backend/Dockerfile",                           BACKEND_DOCKERFILE)

print("\n[4/8] Frontend files...")
mkfile("frontend/.env.example",                       FRONTEND_ENV_EXAMPLE)
mkfile("frontend/vercel.json",                        VERCEL_JSON)
mkfile("frontend/src/services/api.js",                FRONTEND_API)
mkfile("frontend/src/pages/Dashboard.jsx",            "// TODO: main live monitoring dashboard\n")
mkfile("frontend/src/pages/Login.jsx",                "// TODO: ranger login page\n")
mkfile("frontend/src/pages/AlertDetail.jsx",          "// TODO: single alert detail view\n")
mkfile("frontend/src/components/AlertsTable.jsx",     "// TODO: live alerts table component\n")
mkfile("frontend/src/components/ForestMap.jsx",       "// TODO: Leaflet map with sensor markers\n")
mkfile("frontend/src/components/SensorCard.jsx",      "// TODO: per-sensor status card\n")
mkfile("frontend/src/components/Navbar.jsx",          "// TODO: top navigation bar\n")
mkfile("frontend/src/components/BackendStatus.jsx",   "// TODO: error banner when no backend\n")
mkfile("frontend/src/context/AuthContext.jsx",        "// TODO: JWT + user role React context\n")
mkfile("frontend/src/context/AlertContext.jsx",       "// TODO: shared live alerts context\n")
mkfile("frontend/src/hooks/useAlerts.js",             "// TODO: poll /api/alerts every 10s\n")
mkfile("frontend/src/hooks/useSensors.js",            "// TODO: poll /api/sensors/live every 5s\n")
mkfile("frontend/src/hooks/useBackend.js",            "// TODO: resolve backend on app mount\n")
mkfile("frontend/Dockerfile",                         FRONTEND_DOCKERFILE)

print("\n[5/8] Simulator files...")
mkfile("simulator/mqtt_simulator.py",        SIMULATOR_SCRIPT)
mkfile("simulator/requirements.txt",         SIMULATOR_REQUIREMENTS)
mkfile("simulator/tests/__init__.py",        "")
mkfile("simulator/tests/test_simulator.py",  SIMULATOR_TESTS)
mkfile("simulator/Dockerfile",               SIMULATOR_DOCKERFILE)

print("\n[6/8] Database migration files...")
mkfile("database/migrations/001_create_sensor_readings.sql", MIGRATION_001)
mkfile("database/migrations/002_create_alerts.sql",          MIGRATION_002)
mkfile("database/migrations/003_create_users.sql",           MIGRATION_003)
mkfile("database/seeds/dev_seed.sql",                        SEED_SQL)

print("\n[7/8] Updated project-setup-summary.txt...")
overwrite("project-setup-summary.txt", SETUP_SUMMARY)

print("\n[8/8] Done!\n")
print("=" * 60)
print("  SmartForest patch.py completed successfully")
print("=" * 60)
print("""
Files created. Next steps:
  1. cd backend  && cp .env.example .env  (fill Supabase creds)
  2. cd frontend && cp .env.example .env
  3. git add .
  4. git commit -m "chore: full project structure via patch.py"
  5. git push origin develop
     -> CI runs -> all pass -> auto-merge to main -> Vercel deploys
""")
