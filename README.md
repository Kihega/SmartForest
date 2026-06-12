# SmartForest — Illegal Logging Detection System

Real-time monitoring system for detecting illegal logging in Kibiti, Tanzania.

## Stack
- **Backend**: Node.js + Express.js (local or Render.com)
- **Frontend**: React.js / Vite (local or Vercel)
- **Database**: PostgreSQL via Supabase
- **IoT Simulation**: MQTT (Mosquitto broker)

## Quick Start

### 1. MQTT Broker (local)
```bash
sudo apt install mosquitto -y
mosquitto -c mosquitto.conf
```

### 2. Backend
```bash
cd backend && npm install
cp .env.example .env   # fill in Supabase credentials
npm run dev
```

### 3. Frontend
```bash
cd frontend && npm install
cp .env.example .env
npm run dev
```

### 4. Simulator
```bash
cd simulator
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python mqtt_simulator.py
```

## Branching
- `develop` — daily work (local)
- `main` — production (auto-merged after CI passes)
