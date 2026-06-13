# SmartForest — Agile Development Sprints

**Project:** Web-Based System for Detecting Illegal Logging Activities
**Methodology:** Agile (Scrum-inspired, solo developer)
**Sprint Length:** 1 week per sprint
**Branch Strategy:** develop (work) -> main (production via CI/CD)
**Start Date:** June 2026

---

## Notification Strategy

Alerts are delivered via the **web dashboard only** (no email).
Rangers monitoring the dashboard see alerts in real time through:
- Auto-refreshing AlertsTable (polls every 10 seconds)
- Red alert badge counter on the Navbar
- New alert rows highlighted in red with fade-in animation
- Browser Web Notification (popup) when a new alert arrives
- Audio beep sound on new alert (optional, can be toggled off)

---

## Sprint Overview

| Sprint | Focus                           | Status      |
|--------|---------------------------------|-------------|
| 0      | Project Setup & CI/CD           | DONE        |
| 1      | Database Models & Backend Core  | IN PROGRESS |
| 2      | MQTT & Sensor Ingest            | PENDING     |
| 3      | Auth & Security                 | PENDING     |
| 4      | Frontend Dashboard              | PENDING     |
| 5      | Map & Real-Time Alerts          | PENDING     |
| 6      | Dashboard Notifications         | PENDING     |
| 7      | Reporting & Alert Management    | PENDING     |
| 8      | Testing & Hardening             | PENDING     |
| 9      | Deployment & Documentation      | PENDING     |

---

## Sprint 0 — Project Setup & CI/CD
**Duration:** Week 1 | **Status:** DONE

**Goal:** Working skeleton with automated pipeline.

### Completed
- [x] Initialize Git repo with develop/main branch strategy
- [x] Define full folder structure
- [x] Set up Express.js backend skeleton
- [x] Set up React/Vite frontend skeleton
- [x] Set up Python MQTT simulator
- [x] Write 14 passing backend tests (Jest + Supertest)
- [x] Configure GitHub Actions CI/CD pipeline
- [x] Auto-merge develop -> main on all tests passing
- [x] Configure Supabase project and credentials
- [x] Create backend/.env with all credentials
- [x] Deploy backend to Render.com
- [x] Deploy frontend to Vercel

### Definition of Done
- CI pipeline runs green on every push to develop
- /api/health returns 200 on Render cloud URL

---

## Sprint 1 — Database Models & Backend Core
**Duration:** Week 2 | **Status:** IN PROGRESS

**Goal:** Backend reads and writes real data to Supabase.

### User Stories
- As a system, I want to save sensor readings to the database
  so that all historical data is preserved.
- As a ranger, I want to retrieve alerts from the API
  so that the dashboard can display them.
- As a developer, I want DB queries in model files
  so that routes stay clean and testable.

### Tasks
- [ ] Implement sensorModel.js
      saveReading(data)  -> INSERT into sensor_readings
      getAll()           -> SELECT all readings
      getLive()          -> SELECT latest per device_id
- [ ] Implement alertModel.js
      create(data)       -> INSERT into alerts
      getAll()           -> SELECT all ORDER BY created_at DESC
      getById(id)        -> SELECT single alert
      resolve(id)        -> UPDATE status = resolved
      getUnresolved()    -> SELECT where status = unresolved
      countUnresolved()  -> COUNT for navbar badge
- [ ] Implement userModel.js
      getByEmail(email)  -> SELECT user by email
      create(data)       -> INSERT new user profile
- [ ] Wire routes to models
      GET  /api/sensors        -> sensorModel.getAll()
      GET  /api/sensors/live   -> sensorModel.getLive()
      POST /api/sensors        -> sensorModel.saveReading()
      GET  /api/alerts         -> alertModel.getAll()
      GET  /api/alerts/count   -> alertModel.countUnresolved()
      GET  /api/alerts/:id     -> alertModel.getById()
      PATCH /api/alerts/:id/resolve -> alertModel.resolve()
- [ ] Implement errorHandler.js middleware
- [ ] Run SQL migrations on Supabase
- [ ] Update tests to verify real DB responses

### Patch File
    python3 patch_db_models.py

### Definition of Done
- POST /api/sensors saves a row visible in Supabase dashboard
- GET /api/alerts returns real rows (not empty array)
- GET /api/alerts/count returns unresolved alert number
- All 14+ tests still pass

---

## Sprint 2 — MQTT Ingest & Alert Detection
**Duration:** Week 3 | **Status:** PENDING

**Goal:** System automatically detects and stores alerts from sensor data.

### User Stories
- As a forest sensor, I want to publish readings via MQTT
  so that the backend receives them in real time.
- As the system, I want to auto-detect suspicious readings
  so that alerts are created without manual intervention.

### Tasks
- [ ] Wire mqttService.js to call sensorModel.saveReading()
- [ ] Implement alertService.js
      evaluateReading(data)  -> check sound_db and vibration
      if alert -> call alertModel.create()
      deduplicate: skip if same device alerted in last 5 min
- [ ] Wire mqttService -> alertService
- [ ] Test end-to-end locally:
      mosquitto -> simulator -> backend -> Supabase
- [ ] Add MQTT integration test (mock broker)

### Patch File
    python3 patch_mqtt_ingest.py

### Definition of Done
- Simulator running -> readings appear in sensor_readings table
- Sound > 80dB -> row appears in alerts table automatically
- Duplicate alerts within 5 minutes are suppressed

---

## Sprint 3 — Authentication & Authorization
**Duration:** Week 4 | **Status:** PENDING

**Goal:** Only authenticated rangers can access the system.

### User Stories
- As a ranger, I want to log in with email and password
  so that I can access the dashboard securely.
- As the system, I want to reject unauthenticated API calls
  so that data is not publicly accessible.

### Tasks
- [ ] Implement POST /api/auth/login (Supabase Auth)
- [ ] Implement POST /api/auth/logout
- [ ] Implement GET /api/auth/me
- [ ] Implement authMiddleware.js (verify JWT Bearer token)
- [ ] Protect all alert + sensor routes with authMiddleware
- [ ] Update auth tests to cover protected routes
- [ ] Implement AuthContext.jsx in frontend

### Patch File
    python3 patch_auth.py

### Definition of Done
- GET /api/alerts without token returns 401
- POST /api/auth/login with valid creds returns JWT
- GET /api/alerts with valid JWT returns data

---

## Sprint 4 — Frontend Dashboard
**Duration:** Week 5 | **Status:** PENDING

**Goal:** Rangers can log in and see live sensor data.

### User Stories
- As a ranger, I want a login screen to authenticate.
- As a ranger, I want a dashboard showing sensor status
  and recent alerts so I can monitor the forest.

### Tasks
- [ ] Implement Login.jsx (email + password form)
- [ ] Implement useBackend.js (resolve cloud vs local)
- [ ] Implement BackendStatus.jsx (no-backend error banner)
- [ ] Implement Dashboard.jsx layout
      summary cards: total alerts, active sensors, unresolved count
- [ ] Implement SensorCard.jsx
      device_id, zone, last reading, green/red status dot
- [ ] Implement AlertsTable.jsx
      columns: time, zone, device, sound_db, vibration, status
      auto-refresh every 10s via useAlerts hook
- [ ] Implement Navbar.jsx
      logo, ranger name, unresolved alert badge, logout
- [ ] Implement useSensors.js and useAlerts.js hooks

### Patch File
    python3 patch_frontend_dashboard.py

### Definition of Done
- Login works with Supabase ranger credentials
- Dashboard loads sensor cards and alerts table
- Alerts table auto-refreshes every 10 seconds

---

## Sprint 5 — Map & Real-Time Alert Pins
**Duration:** Week 6 | **Status:** PENDING

**Goal:** Visual map showing sensor locations with live alert pins.

### User Stories
- As a ranger, I want sensor locations on a map
  so I know exactly where in the forest to respond.
- As a ranger, I want alert pins to turn red
  so I can immediately spot danger zones.

### Tasks
- [ ] Install leaflet + react-leaflet
- [ ] Implement ForestMap.jsx
      OpenStreetMap tiles centered on Kibiti (-7.78, 38.95)
      green pin = normal, red pin = unresolved alert
      popup: device_id, sound_db, vibration, timestamp
- [ ] Implement AlertContext.jsx (global alert state)
- [ ] Add map to Dashboard.jsx
- [ ] Test map on mobile screen sizes

### Patch File
    python3 patch_map.py

### Definition of Done
- Map renders Kibiti region with sensor pins
- Alert pins turn red within 10 seconds of alert firing
- Clicking a pin shows sensor details popup

---

## Sprint 6 — Dashboard Notifications
**Duration:** Week 7 | **Status:** PENDING

**Goal:** Rangers are alerted instantly via the dashboard UI.
No email — all notifications are web-based only.

### User Stories
- As a ranger watching the dashboard, I want a visible alert
  the moment a new incident is detected so I can respond fast.
- As a ranger, I want the page to notify me even if I am
  on a different browser tab so I don't miss anything.

### Tasks
- [ ] Red badge counter on Navbar showing unresolved alert count
      fetches GET /api/alerts/count every 10s
      badge turns red and pulses when count > 0
- [ ] New alert row highlight in AlertsTable
      new rows flash red for 3 seconds then fade to normal
      'NEW' badge on rows less than 1 minute old
- [ ] Browser Web Notification (Notification API)
      ask permission on login
      fire popup notification when new alert detected
      notification text: 'ALERT: [zone] - Sound [db]dB detected'
      clicking notification focuses the browser tab
- [ ] Audio alert beep (optional, toggle in settings)
      short beep sound when new alert arrives
      toggle on/off button in Navbar
- [ ] Alert toast popup in bottom-right corner
      appears for 5 seconds then auto-dismisses
      shows zone, sensor, sound level

### Patch File
    python3 patch_notifications.py

### Definition of Done
- Navbar badge updates within 10 seconds of new alert
- Browser popup notification fires when alert is created
- Toast appears in bottom-right corner for 5 seconds
- New alert rows highlighted red in the table
- Audio beep fires on new alert (when toggle is ON)

---

## Sprint 7 — Reporting & Alert Management
**Duration:** Week 8 | **Status:** PENDING

**Goal:** Rangers can manage alerts and download reports.

### User Stories
- As a ranger, I want to mark an alert as resolved
  so that the team knows it has been handled.
- As an admin, I want to export all alerts as CSV
  so I can submit evidence to authorities.

### Tasks
- [ ] Implement AlertDetail.jsx page
      full alert info: zone, coords, sound, vibration, timestamp
      Resolve button -> PATCH /api/alerts/:id/resolve
      resolved alerts show green status badge
- [ ] Implement GET /api/reports/alerts (CSV export)
      accepts ?from=date&to=date query params
      returns downloadable CSV file
- [ ] Add Export CSV button to AlertsTable.jsx
- [ ] Add filter controls to AlertsTable
      filter by: zone, status, date range
- [ ] Add pagination to AlertsTable (20 rows per page)

### Patch File
    python3 patch_reporting.py

### Definition of Done
- Resolve button updates alert status in Supabase
- Resolved alerts show green in table and map
- CSV export downloads with correct columns and data

---

## Sprint 8 — Testing & Hardening
**Duration:** Week 9 | **Status:** PENDING

**Goal:** System is robust, secure, and fully tested.

### Tasks
- [ ] Increase backend test coverage to 80%+
- [ ] Add input validation (express-validator)
- [ ] Add rate limiting on auth routes (express-rate-limit)
- [ ] Add security headers (helmet.js)
- [ ] Test all frontend components (React Testing Library)
- [ ] End-to-end test: simulator -> MQTT -> DB -> dashboard
- [ ] Load test: 10 sensors sending data simultaneously

### Patch File
    python3 patch_hardening.py

### Definition of Done
- npm test shows 80%+ coverage
- All security headers present
- System handles 10 concurrent sensors without errors

---

## Sprint 9 — Deployment & Documentation
**Duration:** Week 10 | **Status:** PENDING

**Goal:** System is live, documented, and ready for submission.

### Tasks
- [ ] Verify full cloud stack (Render + Vercel + Supabase)
- [ ] Run final migrations on production Supabase
- [ ] Create ranger user accounts in Supabase Auth
- [ ] Write final README.md with setup instructions
- [ ] Write API documentation (all endpoints + examples)
- [ ] Draw system architecture diagram
- [ ] Record demo video walkthrough
- [ ] Write project report (academic submission)

### Definition of Done
- Frontend live on Vercel, backend live on Render
- Ranger can log in, see map, receive dashboard alert
  triggered by simulator within 10 seconds
- All documentation committed to repo

---

## Patch Files Reference

| Patch File                   | Sprint | Purpose                           |
|------------------------------|--------|-----------------------------------|
| patch.py                     | 0      | Initial project structure         |
| patch_tests.py               | 0      | Add real Jest tests               |
| patch_test_cleanup.py        | 0      | Fix Jest teardown warnings        |
| patch_ci_fix.py              | 0      | Fix auto-merge CI permissions     |
| patch_env.py                 | 0      | Create backend .env               |
| patch_sprints_v2.py          | 0      | This sprints file                 |
| patch_db_models.py           | 1      | DB models + wire routes to DB     |
| patch_mqtt_ingest.py         | 2      | MQTT -> DB + alert detection      |
| patch_auth.py                | 3      | Supabase Auth + JWT middleware    |
| patch_frontend_dashboard.py  | 4      | React dashboard + components      |
| patch_map.py                 | 5      | Leaflet map + alert pins          |
| patch_notifications.py       | 6      | Dashboard alerts + browser notifs |
| patch_reporting.py           | 7      | CSV export + alert management     |
| patch_hardening.py           | 8      | Security + validation + coverage  |

---

## Daily Git Workflow

```bash
# Work on develop branch
git add .
git commit -m "feat: describe what you built"
git push origin develop
# GitHub Actions runs -> all tests pass -> auto-merge to main
# Render redeploys backend, Vercel redeploys frontend
```

## Updating Sprint Progress

```bash
nano SPRINTS.md          # change [ ] to [x] as tasks complete
git add SPRINTS.md
git commit -m "chore: update sprint 1 progress"
git push origin develop
```
