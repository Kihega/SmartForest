#!/usr/bin/env python3
"""
SmartForest — Fix Prisma Connection + Schema Drift
Run: python fix_prisma.py /path/to/SmartForest-main
"""
import os, sys, textwrap, json

def resolve_root():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    candidate = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(candidate, 'backend', 'package.json')):
        return candidate
    sys.exit('Usage: python fix_prisma.py /path/to/SmartForest-main')

ROOT = resolve_root()

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.lstrip('\n'))
    print(f'  OK  {rel}')


# ── 1. Prisma schema (phone removed) ─────────────────────────────────────────
SCHEMA = """
// SmartForest Prisma Schema
// CONNECTION POOLER STRATEGY (Supabase - no direct host needed):
//   DATABASE_URL        -> Transaction pooler port 6543  (runtime queries)
//   DATABASE_URL_DIRECT -> Session pooler     port 5432  (prisma db push/migrate)
//
// Both use aws-0-*.pooler.supabase.com — avoids paid IPv4 add-on for
// the direct db.xxx.supabase.co:5432 host.

generator client {
  provider = "prisma-client-js"
  output   = "../node_modules/.prisma/client"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DATABASE_URL_DIRECT")
}

// phone is stored in Supabase user_metadata — not in this table yet.
// Run 006_add_phone_to_users.sql + uncomment phone field when ready.
model User {
  id         Int      @id @default(autoincrement())
  name       String?  @db.VarChar(100)
  email      String   @unique @db.VarChar(100)
  role       String   @default("customer") @db.VarChar(20)
  createdAt  DateTime @default(now()) @map("created_at")

  devices        Device[]
  resolvedAlerts Alert[]  @relation("ResolvedBy")

  @@map("users")
}

model SensorReading {
  id            Int      @id @default(autoincrement())
  deviceId      String   @db.VarChar(50)  @map("device_id")
  sensorType    String   @default("microphone") @db.VarChar(20) @map("sensor_type")
  zone          String?  @db.VarChar(100)
  latitude      Float?
  longitude     Float?
  soundDb       Decimal? @db.Decimal(5, 2) @map("sound_db")
  flameDetected Boolean  @default(false)   @map("flame_detected")
  temperatureC  Decimal? @db.Decimal(5, 2) @map("temperature_c")
  isAlert       Boolean  @default(false)   @map("is_alert")
  recordedAt    DateTime @default(now())   @map("recorded_at")

  @@index([deviceId],               map: "idx_sr_device")
  @@index([recordedAt(sort: Desc)], map: "idx_sr_time")
  @@index([sensorType],             map: "idx_sr_type")
  @@map("sensor_readings")
}

model Alert {
  id            Int      @id @default(autoincrement())
  deviceId      String?  @db.VarChar(50)  @map("device_id")
  sensorType    String   @default("microphone") @db.VarChar(20) @map("sensor_type")
  alertType     String   @default("illegal_logging") @db.VarChar(30) @map("alert_type")
  zone          String?  @db.VarChar(100)
  latitude      Float?
  longitude     Float?
  soundDb       Decimal? @db.Decimal(5, 2) @map("sound_db")
  flameDetected Boolean  @default(false)   @map("flame_detected")
  temperatureC  Decimal? @db.Decimal(5, 2) @map("temperature_c")
  status        String   @default("unresolved") @db.VarChar(20)
  resolvedById  Int?                            @map("resolved_by")
  createdAt     DateTime @default(now())        @map("created_at")

  resolvedBy    User?    @relation("ResolvedBy", fields: [resolvedById], references: [id])

  @@index([status],                 map: "idx_alerts_status")
  @@index([createdAt(sort: Desc)],  map: "idx_alerts_time")
  @@index([alertType],              map: "idx_alerts_type")
  @@map("alerts")
}

model Device {
  id        Int       @id @default(autoincrement())
  deviceId  String    @unique @db.VarChar(50) @map("device_id")
  ownerId   Int?                               @map("owner_id")
  zone      String?   @db.VarChar(100)
  latitude  Float?
  longitude Float?
  active    Boolean   @default(true)
  lastSeen  DateTime?                          @map("last_seen")
  createdAt DateTime  @default(now())          @map("created_at")

  owner     User?     @relation(fields: [ownerId], references: [id], onDelete: SetNull)

  @@index([ownerId], map: "idx_devices_owner")
  @@index([active],  map: "idx_devices_active")
  @@map("devices")
}
"""
write('backend/prisma/schema.prisma', SCHEMA)


# ── 2. Seed (no phone) ────────────────────────────────────────────────────────
SEED = """
'use strict';
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const admin = await prisma.user.upsert({
    where:  { email: 'admin@smartforest.tz' },
    update: { role: 'admin' },
    create: { name: 'System Admin', email: 'admin@smartforest.tz', role: 'admin' },
  });
  console.log('[seed] Admin:', admin.email, 'id:', admin.id);

  const ranger = await prisma.user.upsert({
    where:  { email: 'john@smartforest.tz' },
    update: {},
    create: { name: 'John Ranger', email: 'john@smartforest.tz', role: 'customer' },
  });
  console.log('[seed] Ranger:', ranger.email, 'id:', ranger.id);

  const readings = [
    { deviceId:'MIC-001',   sensorType:'microphone', zone:'Kibiti-North',
      latitude:-7.72, longitude:38.95, soundDb:42.5,  isAlert:false },
    { deviceId:'MIC-002',   sensorType:'microphone', zone:'Kibiti-South',
      latitude:-7.85, longitude:38.88, soundDb:91.5,  isAlert:true  },
    { deviceId:'FLAME-001', sensorType:'flame', zone:'Kibiti-North',
      latitude:-7.72, longitude:38.95, flameDetected:false, temperatureC:28.5, isAlert:false },
    { deviceId:'FLAME-002', sensorType:'flame', zone:'Kibiti-South',
      latitude:-7.85, longitude:38.88, flameDetected:true,  temperatureC:67.3, isAlert:true  },
  ];
  for (const r of readings) {
    await prisma.sensorReading.create({ data: r });
  }
  console.log('[seed] Created', readings.length, 'sensor readings');

  await prisma.alert.createMany({
    data: [
      { deviceId:'MIC-002',   sensorType:'microphone', alertType:'illegal_logging',
        zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
        soundDb:91.5, status:'unresolved' },
      { deviceId:'FLAME-002', sensorType:'flame', alertType:'fire',
        zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
        flameDetected:true, temperatureC:67.3, status:'unresolved' },
    ],
    skipDuplicates: true,
  });
  console.log('[seed] Created 2 alerts');
  console.log('[seed] Done');
}

main()
  .catch(e => { console.error('[seed] ERROR:', e.message); process.exit(1); })
  .finally(() => prisma.$disconnect());
"""
write('backend/prisma/seed.js', SEED)


# ── 3. userModel (no phone in DB queries) ────────────────────────────────────
USER_MODEL = """
'use strict';
const prisma = require('../config/prisma');
const pool   = require('../config/db');

function toSnake(u) {
  if (!u) return null;
  return {
    id:         u.id,
    name:       u.name,
    email:      u.email,
    role:       u.role,
    created_at: u.createdAt || u.created_at,
  };
}

const userModel = {
  async getByEmail(email) {
    try {
      return toSnake(await prisma.user.findUnique({ where: { email } }));
    } catch (e) {
      console.warn('[userModel] Prisma.getByEmail fallback:', e.message);
      const r = await pool.query('SELECT * FROM users WHERE email=$1', [email]);
      return r.rows[0] || null;
    }
  },

  async getById(id) {
    try {
      return toSnake(await prisma.user.findUnique({ where: { id: Number(id) } }));
    } catch (e) {
      console.warn('[userModel] Prisma.getById fallback:', e.message);
      const r = await pool.query('SELECT * FROM users WHERE id=$1', [id]);
      return r.rows[0] || null;
    }
  },

  async getAll() {
    try {
      const rows = await prisma.user.findMany({ orderBy: { createdAt: 'desc' } });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[userModel] Prisma.getAll fallback:', e.message);
      const r = await pool.query('SELECT * FROM users ORDER BY created_at DESC');
      return r.rows;
    }
  },

  // phone intentionally excluded — not in users table yet.
  // phone is stored in Supabase user_metadata (auth layer).
  async create({ name, email, role }) {
    try {
      return toSnake(await prisma.user.upsert({
        where:  { email },
        update: { name: name || undefined },
        create: { name, email, role: role || 'customer' },
      }));
    } catch (e) {
      console.warn('[userModel] Prisma.create fallback:', e.message);
      const r = await pool.query(
        \`INSERT INTO users (name, email, role)
         VALUES (\$1,\$2,\$3)
         ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
         RETURNING *\`,
        [name, email, role || 'customer']
      );
      return r.rows[0];
    }
  },

  async updateRole(id, role) {
    try {
      return toSnake(await prisma.user.update({
        where: { id: Number(id) },
        data:  { role },
      }));
    } catch (e) {
      console.warn('[userModel] Prisma.updateRole fallback:', e.message);
      const r = await pool.query(
        'UPDATE users SET role=\$1 WHERE id=\$2 RETURNING *', [role, id]
      );
      return r.rows[0] || null;
    }
  },

  async delete(id) {
    try {
      await prisma.user.delete({ where: { id: Number(id) } });
    } catch (e) {
      console.warn('[userModel] Prisma.delete fallback:', e.message);
      await pool.query('DELETE FROM users WHERE id=\$1', [id]);
    }
  },
};

module.exports = userModel;
"""
write('backend/src/models/userModel.js', USER_MODEL)


# ── 4. .env.example (correct pooler URLs) ────────────────────────────────────
ENV_EXAMPLE = """
PORT=5000
NODE_ENV=development

# ── Supabase ───────────────────────────────────────────────────────────────
SUPABASE_URL=https://[REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# ── Database (BOTH use the Supabase POOLER — no direct host needed) ────────
#
# HOW TO GET THESE:
#   Supabase dashboard -> Settings -> Database -> Connection string
#   Use the URI format. Switch between tabs:
#
# DATABASE_URL — "Transaction" tab, port 6543
#   Used by: app at runtime (stateless, fast, PgBouncer transaction mode)
#   Append: ?pgbouncer=true&connection_limit=1
#
DATABASE_URL=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
#
# DATABASE_URL_DIRECT — "Session" tab, port 5432
#   Used by: prisma db push / prisma migrate dev (needs a persistent session for DDL)
#   This is the session pooler — still on aws-0-*.pooler.supabase.com, just port 5432.
#   Do NOT use db.[REF].supabase.co:5432 (requires paid IPv4 add-on).
#
DATABASE_URL_DIRECT=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres

# ── App ────────────────────────────────────────────────────────────────────
JWT_SECRET=your-jwt-secret-change-this
FRONTEND_URL=http://localhost:5173

# ── MQTT ──────────────────────────────────────────────────────────────────
MQTT_BROKER=mqtt://localhost:1883
MQTT_TOPIC=forest/sensor/data

# ── Alert thresholds ───────────────────────────────────────────────────────
SOUND_THRESHOLD_DB=80
TEMP_THRESHOLD_C=55
DEDUP_MINUTES=5
"""
write('backend/.env.example', ENV_EXAMPLE)


# ── 5. Dockerfile ─────────────────────────────────────────────────────────────
DOCKERFILE = """
FROM node:20-alpine
WORKDIR /app

# Build args so prisma generate works at build time without real DB creds.
# Real values are injected at container runtime via environment / env_file.
ARG DATABASE_URL=postgresql://placeholder/placeholder
ARG DATABASE_URL_DIRECT=postgresql://placeholder/placeholder
ENV DATABASE_URL=$DATABASE_URL
ENV DATABASE_URL_DIRECT=$DATABASE_URL_DIRECT

# Copy package files + schema first (layer cache)
COPY package*.json ./
COPY prisma ./prisma/

# Install — postinstall hook runs prisma generate automatically
RUN npm ci --only=production

# Copy remaining source
COPY . .

# Explicit generate (idempotent, ensures client matches schema)
RUN npx prisma generate

EXPOSE 5000
CMD ["node", "src/index.js"]
"""
write('backend/Dockerfile', DOCKERFILE)


# ── 6. GitHub CI workflow ─────────────────────────────────────────────────────
CI = """
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [main]

permissions:
  contents: write

jobs:

  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    env:
      NODE_ENV:             test
      PORT:                 5000
      SUPABASE_URL:         ${{ secrets.SUPABASE_URL }}
      SUPABASE_ANON_KEY:    ${{ secrets.SUPABASE_ANON_KEY }}
      SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
      DATABASE_URL:         ${{ secrets.DATABASE_URL }}
      DATABASE_URL_DIRECT:  ${{ secrets.DATABASE_URL_DIRECT }}
      JWT_SECRET:           ${{ secrets.JWT_SECRET }}
      MQTT_BROKER:          mqtt://localhost:1883
      MQTT_TOPIC:           forest/sensor/data
      SOUND_THRESHOLD_DB:   80
      TEMP_THRESHOLD_C:     55
      DEDUP_MINUTES:        5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: backend/package-lock.json

      - name: Install dependencies
        working-directory: ./backend
        run: npm ci

      # prisma generate only reads schema.prisma and emits JS client.
      # It does NOT connect to the DB, so a placeholder URL is fine for CI.
      - name: Generate Prisma Client
        working-directory: ./backend
        run: npx prisma generate
        env:
          DATABASE_URL:        ${{ secrets.DATABASE_URL || 'postgresql://placeholder/placeholder' }}
          DATABASE_URL_DIRECT: ${{ secrets.DATABASE_URL_DIRECT || 'postgresql://placeholder/placeholder' }}

      - name: Run tests
        working-directory: ./backend
        run: npm test

  test-frontend:
    name: Frontend Lint & Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Lint
        working-directory: ./frontend
        run: npm run lint

      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          VITE_API_URL_CLOUD: ${{ secrets.VITE_API_URL_CLOUD }}
          VITE_API_URL_LOCAL: http://localhost:5000/api

  test-simulator:
    name: Simulator Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install paho-mqtt pytest

      - name: Run simulator tests
        run: pytest simulator/tests/ -v

  docker-build:
    name: Docker Build Check
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4

      - name: Build backend Docker image
        run: |
          docker build ./backend -t smartforest-backend \\
            --build-arg DATABASE_URL="postgresql://placeholder/placeholder" \\
            --build-arg DATABASE_URL_DIRECT="postgresql://placeholder/placeholder"

  # Runs on main branch only — pushes schema to production Supabase DB.
  # Uses session pooler (DATABASE_URL_DIRECT, port 5432) for DDL compatibility.
  prisma-push-prod:
    name: Prisma DB Push (Production)
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, test-simulator, docker-build]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: backend/package-lock.json

      - name: Install dependencies
        working-directory: ./backend
        run: npm ci

      - name: Generate Prisma Client
        working-directory: ./backend
        run: npx prisma generate
        env:
          DATABASE_URL:        ${{ secrets.DATABASE_URL }}
          DATABASE_URL_DIRECT: ${{ secrets.DATABASE_URL_DIRECT }}

      - name: Push schema to production DB
        working-directory: ./backend
        run: npx prisma db push --accept-data-loss
        env:
          DATABASE_URL:        ${{ secrets.DATABASE_URL }}
          DATABASE_URL_DIRECT: ${{ secrets.DATABASE_URL_DIRECT }}

  auto-merge-to-main:
    name: Auto-merge to Main
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, test-simulator, docker-build]
    if: github.ref == 'refs/heads/develop' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Configure Git
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Merge develop into main
        run: |
          git checkout main
          git merge develop --no-ff -m "ci: auto-merge develop into main [skip ci]"
          git push origin main
"""
write('.github/workflows/ci.yml', CI)


# ── 7. Optional SQL: add phone column later ───────────────────────────────────
SQL_006 = """
-- MIGRATION 006: add phone column to users table (OPTIONAL)
-- Run in Supabase SQL Editor only when you want phone stored in the DB.
-- By default phone is stored in Supabase user_metadata (no DB column needed).
--
-- After running this SQL, also:
--   1. Uncomment phone field in backend/prisma/schema.prisma
--   2. Run: npx prisma db push

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS phone VARCHAR(30);
"""
write('database/migrations/006_add_phone_to_users.sql', SQL_006)

# ── 8. README ─────────────────────────────────────────────────────────────────
README = """
# SmartForest — Database & Prisma Guide

## Why two URLs, and why both use the pooler

Supabase exposes Postgres through PgBouncer (the pooler). The raw direct host
`db.[REF].supabase.co:5432` requires a **paid IPv4 add-on** on free-tier projects.

The solution is to use BOTH pooler modes, which are available for free:

| Variable              | Tab in Supabase UI | Port | Used by                     |
|-----------------------|--------------------|------|-----------------------------|
| `DATABASE_URL`        | Transaction        | 6543 | App queries at runtime      |
| `DATABASE_URL_DIRECT` | Session            | 5432 | `prisma db push` / migrate  |

Both URLs point to `aws-0-[region].pooler.supabase.com` — only the port differs.

**Transaction pooler (6543):** Each query may get a different DB connection.
Fast and efficient for read/write app traffic. Append `?pgbouncer=true&connection_limit=1`.

**Session pooler (5432):** One persistent connection per client. Required for
DDL statements (CREATE TABLE, ALTER TABLE) that Prisma migrations use.

### Where to get the URLs
Supabase dashboard → **Settings → Database → Connection string → URI format**

- Click **"Transaction"** tab → copy URI → append `?pgbouncer=true&connection_limit=1`
- Click **"Session"** tab → copy URI → use as-is

---

## First-time setup commands

```bash
cd backend
cp .env.example .env        # edit with your URLs and keys
npm install                 # prisma generate runs automatically via postinstall

# Push schema to DB (creates all tables)
npx prisma db push

# Seed admin user + sample data
npx prisma db seed
```

## Daily commands

| Task                        | Command                       |
|-----------------------------|-------------------------------|
| Apply schema changes        | `npx prisma db push`          |
| Browse data visually        | `npx prisma studio`           |
| Re-run seed                 | `npx prisma db seed`          |
| Regenerate client (after pull) | `npx prisma generate`      |
| Check migration status      | `npx prisma migrate status`   |

## phone column

`phone` is stored in **Supabase user_metadata** (the auth layer).
It does not exist in the `users` DB table by default, which avoids schema
drift with databases created before this column was added.

To add it to the table later:
1. Run `database/migrations/006_add_phone_to_users.sql` in Supabase SQL Editor
2. Uncomment `phone String? @db.VarChar(30)` in `prisma/schema.prisma`
3. Run `npx prisma db push`

## GitHub Secrets required

Go to: GitHub repo → Settings → Secrets and variables → Actions → New secret

| Secret                | Value                                                      |
|-----------------------|------------------------------------------------------------|
| `DATABASE_URL`        | Transaction pooler URI (port 6543) + pgbouncer params      |
| `DATABASE_URL_DIRECT` | Session pooler URI (port 5432)                             |
| `SUPABASE_URL`        | `https://[REF].supabase.co`                                |
| `SUPABASE_ANON_KEY`   | from Supabase → Settings → API                             |
| `SUPABASE_SERVICE_KEY`| from Supabase → Settings → API (service_role key)          |
| `JWT_SECRET`          | any long random string                                     |
| `VITE_API_URL_CLOUD`  | `https://your-render-app.onrender.com/api`                 |

## Manual SQL fallback (if Prisma can't connect at all)

Run these files in order via Supabase SQL Editor:
```
001_create_users.sql
002_create_sensor_readings.sql
003_create_alerts.sql
004_create_devices.sql
005_admin_seed.sql
```
"""
write('database/prisma_fallback_README.md', README)

# ── 9. Print summary ─────────────────────────────────────────────────────────
print()
print('=' * 65)
print('  fix_prisma patch applied!')
print('=' * 65)
print()
print('WHAT WAS FIXED:')
print()
print('  ERROR 1 — P1001 (can\'t reach db.xxx.supabase.co:5432)')
print('    DATABASE_URL_DIRECT now uses the SESSION POOLER')
print('    (aws-0-*.pooler.supabase.com:5432) instead of the')
print('    direct Supabase host that requires a paid IPv4 add-on.')
print()
print('  ERROR 2 — P2022 (column users.phone does not exist)')
print('    Removed phone from schema.prisma and all model/seed code.')
print('    phone is stored in Supabase user_metadata instead.')
print('    Optional 006_add_phone_to_users.sql provided for later.')
print()
print('FILES CHANGED:')
print('  backend/prisma/schema.prisma              (phone removed)')
print('  backend/prisma/seed.js                    (phone removed)')
print('  backend/src/models/userModel.js           (phone removed)')
print('  backend/.env.example                      (pooler URL docs)')
print('  backend/Dockerfile                        (placeholder build args)')
print('  .github/workflows/ci.yml                  (session pooler for CI)')
print('  database/migrations/006_add_phone_to_users.sql  [new, optional]')
print('  database/prisma_fallback_README.md        [updated]')
print()
print('NOW DO THIS:')
print()
print('  Step 1 — Update your .env:')
print()
print('    DATABASE_URL=postgresql://postgres.[REF]:[PW]@')
print('      aws-0-eu-west-1.pooler.supabase.com:6543/postgres')
print('      ?pgbouncer=true&connection_limit=1')
print()
print('    DATABASE_URL_DIRECT=postgresql://postgres.[REF]:[PW]@')
print('      aws-0-eu-west-1.pooler.supabase.com:5432/postgres')
print()
print('    (Get both from: Supabase → Settings → Database →')
print('     Connection string → Transaction tab / Session tab)')
print()
print('  Step 2 — Push schema and seed:')
print('    npx prisma db push')
print('    npx prisma db seed')
print()
print('  Step 3 — Run tests:')
print('    npm test')
print()
print('Done!')

