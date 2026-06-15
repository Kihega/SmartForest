#!/usr/bin/env python3
"""
SmartForest MQTT IoT Simulator

Simulates TWO sensor types in Kibiti forest zones:

  MICROPHONE sensors (MIC-001 to MIC-003)
    -> Detect abnormal sounds such as chainsaw noise
    -> Associated with illegal logging activities
    -> Field: sound_db (alert if > 80 dB)

  FLAME sensors (FLAME-001 to FLAME-002)
    -> Detect fire incidents within forest areas
    -> Fields: flame_detected (bool) + temperature_c (alert if > 55C)

Backend detection order:
  1. Try BACKEND_URL env var (if set manually)
  2. Try Render.com cloud URL (CLOUD_BACKEND_URL env var)
  3. Fall back to local backend (http://localhost:5000)

Usage:
  source venv/bin/activate
  python mqtt_simulator.py

Env vars:
  MQTT_BROKER_HOST    default: localhost
  MQTT_BROKER_PORT    default: 1883
  MQTT_TOPIC          default: forest/sensor/data
  CLOUD_BACKEND_URL   your Render backend URL
  SEND_INTERVAL       default: 5 (seconds)
  SPIKE_CHANCE        default: 0.20
"""

import paho.mqtt.client as mqtt
import json, random, time, os, sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ───────────────────────────────────────────────
BROKER       = os.getenv('MQTT_BROKER_HOST',   'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC',          'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL',  5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE',   0.20))
CLOUD_URL    = os.getenv('CLOUD_BACKEND_URL',   '').rstrip('/')
LOCAL_URL    = 'http://localhost:5000'

# ── Sensor definitions ───────────────────────────────────
ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
]

MICROPHONE_SENSORS = ['MIC-001', 'MIC-002', 'MIC-003']
FLAME_SENSORS      = ['FLAME-001', 'FLAME-002']

# ── Backend health check ─────────────────────────────────
def check_backend(url, timeout=4):
    try:
        req = urllib.request.urlopen(
            url + '/api/health', timeout=timeout
        )
        return req.status == 200
    except Exception:
        return False

def resolve_backend():
    manual = os.getenv('BACKEND_URL', '').rstrip('/')
    if manual:
        if check_backend(manual):
            print(f'[SIM] Backend: manual override -> {manual}')
            return manual
        print(f'[SIM] WARNING: BACKEND_URL {manual} is not reachable')

    if CLOUD_URL:
        if check_backend(CLOUD_URL):
            print(f'[SIM] Backend: cloud (Render) -> {CLOUD_URL}')
            return CLOUD_URL
        print(f'[SIM] Cloud backend unreachable: {CLOUD_URL}')

    if check_backend(LOCAL_URL, timeout=2):
        print(f'[SIM] Backend: local -> {LOCAL_URL}')
        return LOCAL_URL

    print('[SIM] WARNING: No backend reachable.')
    print('      Data will be published to MQTT only.')
    print('      Start backend: cd backend && npm run dev')
    return None

# ── Payload generators ───────────────────────────────────
def make_microphone_payload(spike):
    zone = random.choice(ZONES)
    return {
        'device_id'   : random.choice(MICROPHONE_SENSORS),
        'sensor_type' : 'microphone',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : zone['zone'],
        'latitude'    : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'   : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        # Normal ambient forest sound: 20-60 dB
        # Chainsaw / illegal logging:  82-98 dB  (alert threshold: 80 dB)
        'sound_db'    : round(
            random.uniform(82, 98) if spike
            else random.uniform(20, 60), 2
        ),
    }

def make_flame_payload(spike):
    zone = random.choice(ZONES)
    fire = spike
    return {
        'device_id'      : random.choice(FLAME_SENSORS),
        'sensor_type'    : 'flame',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : zone['zone'],
        'latitude'       : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        # Normal forest temp: 22-40 C
        # Fire detected:      58-95 C  (alert threshold: 55 C)
        'flame_detected' : fire,
        'temperature_c'  : round(
            random.uniform(58, 95) if fire
            else random.uniform(22, 40), 2
        ),
    }

# ── HTTP POST to backend (redundant delivery) ────────────
def post_to_backend(backend_url, payload):
    if not backend_url:
        return
    try:
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            backend_url + '/api/sensors',
            data    = data,
            headers = {'Content-Type': 'application/json'},
            method  = 'POST'
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')

# ── MQTT callbacks ───────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'[MQTT] Connected to broker at {BROKER}:{PORT}')
    else:
        print(f'[MQTT] Connection failed: reason code {reason_code}')
        sys.exit(1)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f'[MQTT] Disconnected ({reason_code}) - retrying...')

# ── Setup MQTT client ────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect    = on_connect
client.on_disconnect = on_disconnect

print('[SIM] SmartForest Simulator starting...')
print(f'[SIM] Sensor types: MICROPHONE (chainsaw/logging) + FLAME (fire)')
print()

# ── Resolve backend URL ──────────────────────────────────
backend_url = resolve_backend()

# ── Connect to MQTT broker ───────────────────────────────
print(f'[MQTT] Connecting to {BROKER}:{PORT} ...')
try:
    client.connect(BROKER, PORT, keepalive=60)
except Exception as e:
    print(f'[MQTT] ERROR: Cannot connect -> {e}')
    print('       Start Mosquitto: sudo apt install mosquitto -y')
    print('       Then run: mosquitto -c mosquitto.conf')
    sys.exit(1)

client.loop_start()
time.sleep(1)

print(f'[SIM] Topic    : {TOPIC}')
print(f'[SIM] Interval : {INTERVAL}s | Spike chance: {int(SPIKE_CHANCE*100)}%')
print(f'[SIM] Press Ctrl+C to stop')
print('-' * 65)

readings = 0
alerts   = 0

try:
    while True:
        spike = random.random() < SPIKE_CHANCE

        # Alternate between microphone and flame sensor each cycle
        # so both types flow into the DB regularly
        if readings % 2 == 0:
            payload = make_microphone_payload(spike)
            label   = (
                f"LOGGING-ALERT sound:{payload['sound_db']}dB"
                if spike else
                f"mic-ok   sound:{payload['sound_db']}dB"
            )
        else:
            payload = make_flame_payload(spike)
            label   = (
                f"FIRE-ALERT   temp:{payload['temperature_c']}C flame:YES"
                if spike else
                f"flame-ok temp:{payload['temperature_c']}C"
            )

        # 1. Publish to MQTT (backend subscribes)
        client.publish(TOPIC, json.dumps(payload))

        # 2. Also POST directly to backend HTTP (redundancy)
        post_to_backend(backend_url, payload)

        readings += 1
        if spike:
            alerts += 1

        ts = datetime.now().strftime('%H:%M:%S')
        print(
            f"{ts} | {label:<45} | "
            f"{payload['zone']:<14} | "
            f"r:{readings} a:{alerts}"
        )

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print(f'\n[SIM] Stopped. Readings: {readings} | Alerts triggered: {alerts}')
    client.loop_stop()
    client.disconnect()
