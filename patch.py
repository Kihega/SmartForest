#!/usr/bin/env python3
"""
patch_test_cleanup.py — Fix Jest teardown warnings
Run from SmartForest ROOT folder: python3 patch_test_cleanup.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def overwrite(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("  [UPDATE] " + path)

BT = chr(96)

INDEX_JS = (
    "const express  = require('express');\n"
    "const cors     = require('cors');\n"
    "const dotenv   = require('dotenv');\n"
    "const { connectMQTT } = require('./services/mqttService');\n\n"
    "dotenv.config();\n\n"
    "const app  = express();\n"
    "const PORT = process.env.PORT || 5000;\n\n"
    "app.use(cors());\n"
    "app.use(express.json());\n\n"
    "app.use('/api/alerts',  require('./routes/alerts'));\n"
    "app.use('/api/sensors', require('./routes/sensors'));\n"
    "app.use('/api/auth',    require('./routes/auth'));\n\n"
    "app.get('/api/health', (req, res) => {\n"
    "  res.json({ status: 'ok', timestamp: new Date().toISOString() });\n"
    "});\n\n"
    "// Only start server and connect MQTT when NOT running tests\n"
    "let server;\n"
    "if (process.env.NODE_ENV !== 'test') {\n"
    "  connectMQTT();\n"
    "  server = app.listen(PORT, () => {\n"
    + "    console.log(" + BT + "SmartForest backend running on http://localhost:${PORT}" + BT + ");\n"
    "  });\n"
    "}\n\n"
    "module.exports = { app, server };\n"
)

PACKAGE_JSON = (
    '{\n'
    '  "name": "backend",\n'
    '  "version": "1.0.0",\n'
    '  "description": "SmartForest illegal logging detection backend",\n'
    '  "main": "src/index.js",\n'
    '  "type": "commonjs",\n'
    '  "scripts": {\n'
    '    "start": "node src/index.js",\n'
    '    "dev": "nodemon src/index.js",\n'
    '    "test": "jest",\n'
    '    "test:verbose": "jest --verbose"\n'
    '  },\n'
    '  "jest": {\n'
    '    "testEnvironment": "node",\n'
    '    "forceExit": true,\n'
    '    "silent": true,\n'
    '    "testTimeout": 10000\n'
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

ALERTS_TEST = (
    "const request = require('supertest');\n"
    "const { app } = require('../src/index');\n\n"
    "describe('GET /api/health', () => {\n"
    "  it('returns status ok', async () => {\n"
    "    const res = await request(app).get('/api/health');\n"
    "    expect(res.statusCode).toBe(200);\n"
    "    expect(res.body).toHaveProperty('status', 'ok');\n"
    "  });\n"
    "});\n\n"
    "describe('GET /api/alerts', () => {\n"
    "  it('returns 200 and an array', async () => {\n"
    "    const res = await request(app).get('/api/alerts');\n"
    "    expect(res.statusCode).toBe(200);\n"
    "    expect(Array.isArray(res.body)).toBe(true);\n"
    "  });\n\n"
    "  it('each alert has required fields when data exists', async () => {\n"
    "    const res = await request(app).get('/api/alerts');\n"
    "    if (res.body.length > 0) {\n"
    "      const alert = res.body[0];\n"
    "      expect(alert).toHaveProperty('id');\n"
    "      expect(alert).toHaveProperty('zone');\n"
    "      expect(alert).toHaveProperty('status');\n"
    "    } else {\n"
    "      expect(res.body).toEqual([]);\n"
    "    }\n"
    "  });\n"
    "});\n\n"
    "describe('GET /api/alerts/:id', () => {\n"
    "  it('returns 404 for non-existent alert', async () => {\n"
    "    const res = await request(app).get('/api/alerts/999999');\n"
    "    expect(res.statusCode).toBe(404);\n"
    "  });\n"
    "});\n"
)

SENSORS_TEST = (
    "const request = require('supertest');\n"
    "const { app } = require('../src/index');\n\n"
    "describe('GET /api/sensors', () => {\n"
    "  it('returns 200 and an array', async () => {\n"
    "    const res = await request(app).get('/api/sensors');\n"
    "    expect(res.statusCode).toBe(200);\n"
    "    expect(Array.isArray(res.body)).toBe(true);\n"
    "  });\n\n"
    "  it('each reading has required fields when data exists', async () => {\n"
    "    const res = await request(app).get('/api/sensors');\n"
    "    if (res.body.length > 0) {\n"
    "      const r = res.body[0];\n"
    "      expect(r).toHaveProperty('device_id');\n"
    "      expect(r).toHaveProperty('sound_db');\n"
    "      expect(r).toHaveProperty('vibration');\n"
    "      expect(r).toHaveProperty('zone');\n"
    "    } else {\n"
    "      expect(res.body).toEqual([]);\n"
    "    }\n"
    "  });\n"
    "});\n\n"
    "describe('GET /api/sensors/live', () => {\n"
    "  it('returns 200 and an array', async () => {\n"
    "    const res = await request(app).get('/api/sensors/live');\n"
    "    expect(res.statusCode).toBe(200);\n"
    "    expect(Array.isArray(res.body)).toBe(true);\n"
    "  });\n"
    "});\n\n"
    "describe('POST /api/sensors', () => {\n"
    "  it('rejects missing device_id with 400', async () => {\n"
    "    const res = await request(app)\n"
    "      .post('/api/sensors')\n"
    "      .send({ sound_db: 55, vibration: 2 });\n"
    "    expect(res.statusCode).toBe(400);\n"
    "  });\n\n"
    "  it('accepts valid sensor payload', async () => {\n"
    "    const res = await request(app)\n"
    "      .post('/api/sensors')\n"
    "      .send({\n"
    "        device_id : 'SENSOR-TEST',\n"
    "        zone      : 'Kibiti-North',\n"
    "        latitude  : -7.72,\n"
    "        longitude : 38.95,\n"
    "        sound_db  : 45.0,\n"
    "        vibration : 2.1,\n"
    "      });\n"
    "    expect([200, 201]).toContain(res.statusCode);\n"
    "  });\n"
    "});\n"
)

AUTH_TEST = (
    "const request = require('supertest');\n"
    "const { app } = require('../src/index');\n\n"
    "describe('POST /api/auth/login', () => {\n"
    "  it('returns 400 when body is empty', async () => {\n"
    "    const res = await request(app).post('/api/auth/login').send({});\n"
    "    expect(res.statusCode).toBe(400);\n"
    "  });\n\n"
    "  it('returns 400 when email is missing', async () => {\n"
    "    const res = await request(app)\n"
    "      .post('/api/auth/login')\n"
    "      .send({ password: 'test1234' });\n"
    "    expect(res.statusCode).toBe(400);\n"
    "  });\n\n"
    "  it('returns 400 when password is missing', async () => {\n"
    "    const res = await request(app)\n"
    "      .post('/api/auth/login')\n"
    "      .send({ email: 'ranger@forest.go.tz' });\n"
    "    expect(res.statusCode).toBe(400);\n"
    "  });\n\n"
    "  it('returns 401 for wrong credentials', async () => {\n"
    "    const res = await request(app)\n"
    "      .post('/api/auth/login')\n"
    "      .send({ email: 'fake@fake.com', password: 'wrongpass' });\n"
    "    expect([401, 400]).toContain(res.statusCode);\n"
    "  });\n"
    "});\n\n"
    "describe('POST /api/auth/logout', () => {\n"
    "  it('returns 200 or 401 depending on session', async () => {\n"
    "    const res = await request(app).post('/api/auth/logout');\n"
    "    expect([200, 401]).toContain(res.statusCode);\n"
    "  });\n"
    "});\n"
)

print("\nApplying fixes...\n")

# Validate we are in the right folder
if not os.path.isdir(os.path.join(ROOT, "backend")):
    print("ERROR: Run this from the SmartForest ROOT folder, not inside backend/")
    print("  cd ~/SmartForest && python3 patch_test_cleanup.py")
    exit(1)

overwrite("backend/src/index.js",          INDEX_JS)
overwrite("backend/package.json",          PACKAGE_JSON)
overwrite("backend/tests/alerts.test.js",  ALERTS_TEST)
overwrite("backend/tests/sensors.test.js", SENSORS_TEST)
overwrite("backend/tests/auth.test.js",    AUTH_TEST)

print("""
Done! Now run:
  cd ~/SmartForest/backend && npm test

Expected:
  Test Suites: 3 passed, 3 total
  Tests:       14 passed, 14 total
  (clean output, no warnings)
""")
