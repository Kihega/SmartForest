# Hosting the Simulator on Render

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
docker run --rm \
  -e BACKEND_URL=http://host.docker.internal:5000 \
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
