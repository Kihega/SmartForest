#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates REAL hardware units. Each simulator device is labeled with a
# hardware-style ID:
#   Real hardware units  : smf-01a, smf-02a, smf-03a (SmartForest devices)
#   Simulator units      : smt-01a, smt-02a, smt-03a (simulator = "smt")

# Sensor types simulated:
#   MICROPHONE  - chainsaw / illegal logging detection  (alert threshold: 80 dB)
#   FLAME       - fire detection  (alert threshold: 55C or flame_detected=True)
#
# Usage:
#   pip install paho-mqtt --break-system-packages
#   python mqtt_simulator.py               # start (default 5-second interval)
#   python mqtt_simulator.py --stop        # graceful stop via sentinel file
#   SEND_INTERVAL=2 SPIKE_CHANCE=0.30 python mqtt_simulator.py
#
# Control signals:
#   Create a file named STOP_SIMULATOR in the same directory to stop the loop.
#   The script removes the file and exits cleanly.
#
# Env vars:
#   MQTT_BROKER_HOST    default: localhost
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   CLOUD_BACKEND_URL   Render / cloud backend URL
#   BACKEND_URL         manual override backend URL
#   SEND_INTERVAL       default: 5 (seconds between readings)
#   SPIKE_CHANCE        default: 0.20  (probability of alert-level reading)
#   USE_REAL_IDS        default: false  (set to "true" to use smf-* IDs)

import paho.mqtt.client as mqtt
import json, random, time, os, sys, argparse, signal
from datetime import datetime, timezone
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
BROKER       = os.getenv('MQTT_BROKER_HOST',   'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC',          'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL',  5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE',   0.20))
CLOUD_URL    = os.getenv('CLOUD_BACKEND_URL',   '').rstrip('/')
LOCAL_URL    = 'http://localhost:5000'

# Hardware ID prefix
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
MIC_PREFIX   = 'smf' if USE_REAL_IDS else 'smt'
FLM_PREFIX   = 'smf' if USE_REAL_IDS else 'smt'

SENTINEL = Path(__file__).parent / 'STOP_SIMULATOR'

# ── Sensor definitions ───────────────────────────────────────────────────────
ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
    {'zone': 'Kibiti-West',  'lat': -7.80, 'lng': 38.82},
]

# Hardware unit IDs
MIC_SENSORS   = [f'{MIC_PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_SENSORS = [f'{FLM_PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

import urllib.request, urllib.error

# ── Backend health check ──────────────────────────────────────────────────────
def check_backend(url, timeout=4):
    try:
        req = urllib.request.urlopen(url + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception:
        return False

def resolve_backend():
    manual = os.getenv('BACKEND_URL', '').rstrip('/')
    if manual and check_backend(manual):
        print(f'[SIM] Backend: manual override -> {manual}')
        return manual
    if CLOUD_URL and check_backend(CLOUD_URL):
        print(f'[SIM] Backend: cloud -> {CLOUD_URL}')
        return CLOUD_URL
    if check_backend(LOCAL_URL, timeout=2):
        print(f'[SIM] Backend: local -> {LOCAL_URL}')
        return LOCAL_URL
    print('[SIM] No backend reachable — MQTT only mode')
    return None

# ── Payload generators ────────────────────────────────────────────────────────
def make_microphone_payload(spike):
    zone = random.choice(ZONES)
    device = random.choice(MIC_SENSORS)
    return {
        'device_id'   : device,
        'sensor_type' : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : zone['zone'],
        'latitude'    : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'   : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'    : round(
            random.uniform(82, 98) if spike else random.uniform(20, 60), 2
        ),
    }

def make_flame_payload(spike):
    zone = random.choice(ZONES)
    device = random.choice(FLAME_SENSORS)
    return {
        'device_id'      : device,
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : zone['zone'],
        'latitude'       : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : spike,
        'temperature_c'  : round(
            random.uniform(58, 95) if spike else random.uniform(22, 40), 2
        ),
    }

# ── HTTP fallback ─────────────────────────────────────────────────────────────
def post_to_backend(backend_url, payload):
    if not backend_url:
        return
    try:
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            backend_url + '/api/sensors',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')

# ── MQTT callbacks ────────────────────────────────────────────────────────────
_running = True

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'[MQTT] Connected to broker at {BROKER}:{PORT}')
    else:
        print(f'[MQTT] Connection failed: reason code {reason_code}')
        sys.exit(1)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f'[MQTT] Disconnected ({reason_code}) — retrying...')

def graceful_stop(sig, frame):
    global _running
    print('\n[SIM] Signal received — stopping...')
    _running = False

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Hardware Simulator')
    p.add_argument('--stop', action='store_true',
                   help='Create STOP_SIMULATOR sentinel to stop a running instance')
    p.add_argument('--interval', type=float, default=INTERVAL,
                   help=f'Seconds between readings (default {INTERVAL})')
    p.add_argument('--spike',    type=float, default=SPIKE_CHANCE,
                   help=f'Alert spike probability 0–1 (default {SPIKE_CHANCE})')
    p.add_argument('--real-hw',  action='store_true',
                   help='Use smf-* IDs (real hardware IDs) instead of smt-* (simulator)')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _running, USE_REAL_IDS, MIC_SENSORS, FLAME_SENSORS, INTERVAL, SPIKE_CHANCE

    args = parse_args()

    if args.stop:
        SENTINEL.touch()
        print(f'[SIM] Created stop signal: {SENTINEL}')
        print('[SIM] The running simulator will stop at next cycle.')
        return

    INTERVAL     = args.interval
    SPIKE_CHANCE = args.spike
    if args.real_hw:
        USE_REAL_IDS = True
        MIC_SENSORS   = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_SENSORS = [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    hw_label = 'REAL HARDWARE' if USE_REAL_IDS else 'SIMULATOR (labeled as real HW)'
    print('[SIM] SmartForest IoT Hardware Simulator')
    print(f'[SIM] Hardware type : {hw_label}')
    print(f'[SIM] MIC  units    : {MIC_SENSORS}')
    print(f'[SIM] FLAME units   : {FLAME_SENSORS}')
    print(f'[SIM] Interval      : {INTERVAL}s | Spike chance: {int(SPIKE_CHANCE*100)}%')
    print()

    # Remove stale sentinel
    if SENTINEL.exists():
        SENTINEL.unlink()

    backend_url = resolve_backend()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect

    print(f'[MQTT] Connecting to {BROKER}:{PORT} ...')
    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f'[MQTT] ERROR: Cannot connect -> {e}')
        print('       Start Mosquitto: mosquitto -c mosquitto.conf')
        sys.exit(1)

    client.loop_start()
    time.sleep(1)

    print(f'[SIM] Topic : {TOPIC}')
    print(f'[SIM] Press Ctrl+C or run: python mqtt_simulator.py --stop')
    print('-' * 70)

    readings = 0
    alerts   = 0

    while _running:
        # Check sentinel file
        if SENTINEL.exists():
            print(f'[SIM] Stop sentinel detected. Exiting...')
            SENTINEL.unlink()
            break

        spike   = random.random() < SPIKE_CHANCE
        is_mic  = readings % 2 == 0

        if is_mic:
            payload = make_microphone_payload(spike)
            label   = (
                f"LOGGING-ALERT  {payload['device_id']}  sound:{payload['sound_db']}dB"
                if spike else
                f"mic-normal     {payload['device_id']}  sound:{payload['sound_db']}dB"
            )
        else:
            payload = make_flame_payload(spike)
            label   = (
                f"FIRE-ALERT     {payload['device_id']}  temp:{payload['temperature_c']}C"
                if spike else
                f"flame-normal   {payload['device_id']}  temp:{payload['temperature_c']}C"
            )

        client.publish(TOPIC, json.dumps(payload))
        post_to_backend(backend_url, payload)

        readings += 1
        if spike:
            alerts += 1

        ts = datetime.now().strftime('%H:%M:%S')
        print(f"{ts} | {label:<55} | {payload['zone']:<14} | r:{readings} a:{alerts}")

        time.sleep(INTERVAL)

    print(f'\n[SIM] Stopped. Readings: {readings} | Alerts triggered: {alerts}')
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    main()
