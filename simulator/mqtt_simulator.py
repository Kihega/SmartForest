
#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates real hardware sensor units that:
#   1. Publish MQTT messages  -> backend MQTT broker -> saved to DB
#   2. POST directly to backend REST API             -> saved to DB (HTTP fallback)
#
# Hardware ID convention:
#   Real hardware : smf-m01a (microphone), smf-f01a (flame)
#   Simulator     : smt-m01a (microphone), smt-f01a (flame)
#
# Backend URL resolution (reads from .env — never hardcoded):
#   Priority: BACKEND_URL_LOCAL -> BACKEND_URL_CLOUD -> BACKEND_URL_EXTRA
#
# Usage:
#   pip install paho-mqtt python-dotenv
#   python mqtt_simulator.py            # run with defaults
#   python mqtt_simulator.py --stop     # graceful stop
#   python mqtt_simulator.py --interval 2 --spike 0.4
#   USE_REAL_IDS=true python mqtt_simulator.py
#
# Env vars (set in simulator/.env or export before running):
#   BACKEND_URL_LOCAL   default: http://localhost:5000
#   BACKEND_URL_CLOUD   cloud backend URL
#   BACKEND_URL_EXTRA   optional third fallback
#   MQTT_BROKER_HOST    default: localhost
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   SEND_INTERVAL       default: 5 (seconds)
#   SPIKE_CHANCE        default: 0.20
#   USE_REAL_IDS        default: false

import paho.mqtt.client as mqtt
import json, random, time, os, sys, argparse, signal, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Load .env if python-dotenv is available ───────────────────────────────────
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        env_file = Path(__file__).parent.parent / 'backend' / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f'[SIM] Loaded env: {env_file}')
except ImportError:
    pass   # python-dotenv optional

# ── Config from env (never hardcoded URLs) ────────────────────────────────────
BACKEND_CANDIDATES = [
    url for url in [
        os.getenv('BACKEND_URL_LOCAL', 'http://localhost:5000').rstrip('/'),
        os.getenv('BACKEND_URL_CLOUD', '').rstrip('/'),
        os.getenv('BACKEND_URL_EXTRA', '').rstrip('/'),
    ] if url
]
# Remove duplicates preserving order
seen = set()
BACKEND_CANDIDATES = [u for u in BACKEND_CANDIDATES if u not in seen and not seen.add(u)]

BROKER       = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC',        'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL', 5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE',  0.20))
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
SENTINEL     = Path(__file__).parent / 'STOP_SIMULATOR'

PREFIX   = 'smf' if USE_REAL_IDS else 'smt'
MIC_IDS  = [f'{PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_IDS= [f'{PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

ZONES = [
    {'zone':'Kibiti-North', 'lat':-7.72, 'lng':38.95},
    {'zone':'Kibiti-South', 'lat':-7.85, 'lng':38.88},
    {'zone':'Kibiti-East',  'lat':-7.78, 'lng':39.05},
    {'zone':'Kibiti-West',  'lat':-7.80, 'lng':38.82},
]

# ── Backend probe + resolver ──────────────────────────────────────────────────
def probe(base_url, timeout=3):
    try:
        req = urllib.request.urlopen(base_url + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception:
        return False

def resolve_backend():
    for url in BACKEND_CANDIDATES:
        t = 2 if 'localhost' in url else 5
        if probe(url, t):
            print(f'[SIM] Backend resolved: {url}')
            return url
        print(f'[SIM] Backend unreachable: {url}')
    print('[SIM] No backend reachable — MQTT-only mode')
    return None

# ── Payload generators ────────────────────────────────────────────────────────
def make_mic(spike):
    z = random.choice(ZONES)
    return {
        'device_id'   : random.choice(MIC_IDS),
        'sensor_type' : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : z['zone'],
        'latitude'    : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'   : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'    : round(random.uniform(82, 98) if spike else random.uniform(20, 60), 2),
    }

def make_flame(spike):
    z = random.choice(ZONES)
    return {
        'device_id'      : random.choice(FLAME_IDS),
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : z['zone'],
        'latitude'       : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : spike,
        'temperature_c'  : round(random.uniform(58, 95) if spike else random.uniform(22, 40), 2),
    }

# ── HTTP POST to backend ──────────────────────────────────────────────────────
def post_reading(backend_url, payload):
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
        urllib.request.urlopen(req, timeout=4)
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')

# ── MQTT callbacks ────────────────────────────────────────────────────────────
_running = True

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print(f'[MQTT] Connected: {BROKER}:{PORT}  topic: {TOPIC}')
    else:
        print(f'[MQTT] Connect failed rc={rc}')

def on_disconnect(client, userdata, flags, rc, props=None):
    if rc != 0:
        print(f'[MQTT] Disconnected rc={rc} — will retry')

def graceful_stop(sig, frame):
    global _running
    print('
[SIM] Stopping...')
    _running = False

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Simulator')
    p.add_argument('--stop',     action='store_true', help='Stop a running instance')
    p.add_argument('--interval', type=float, default=INTERVAL)
    p.add_argument('--spike',    type=float, default=SPIKE_CHANCE)
    p.add_argument('--real-hw',  action='store_true', help='Use smf-* IDs')
    p.add_argument('--http-only',action='store_true', help='Skip MQTT, use HTTP only')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
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
        PREFIX   = 'smf'
        MIC_IDS  = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_IDS= [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    if SENTINEL.exists():
        SENTINEL.unlink()

    hw_label = 'REAL HW' if USE_REAL_IDS else 'SIMULATOR'
    print('=' * 60)
    print('  SmartForest IoT Simulator')
    print('=' * 60)
    print(f'  Mode     : {hw_label}')
    print(f'  MIC IDs  : {MIC_IDS}')
    print(f'  FLAME IDs: {FLAME_IDS}')
    print(f'  Interval : {INTERVAL}s  |  Spike: {int(SPIKE_CHANCE*100)}%')
    print(f'  Backends : {BACKEND_CANDIDATES}')
    print()

    backend_url = resolve_backend()

    # MQTT setup (optional — skipped with --http-only)
    client = None
    if not args.http_only:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect    = on_connect
            client.on_disconnect = on_disconnect
            client.connect(BROKER, PORT, keepalive=60)
            client.loop_start()
            time.sleep(1.0)
            print(f'[MQTT] Broker: {BROKER}:{PORT}')
        except Exception as e:
            print(f'[MQTT] Cannot connect: {e}')
            print('[MQTT] Falling back to HTTP-only mode')
            client = None

    print()
    print('  Ctrl+C  or  python mqtt_simulator.py --stop  to exit')
    print('-' * 60)

    reads = 0
    alerts_sent = 0

    while _running:
        if SENTINEL.exists():
            SENTINEL.unlink()
            print('[SIM] Stop sentinel detected — exiting cleanly')
            break

        spike   = random.random() < SPIKE_CHANCE
        use_mic = reads % 2 == 0
        payload = make_mic(spike) if use_mic else make_flame(spike)

        # MQTT publish
        if client:
            try:
                client.publish(TOPIC, json.dumps(payload))
            except Exception as e:
                print(f'  [MQTT] Publish failed: {e}')

        # HTTP POST to backend
        post_reading(backend_url, payload)

        reads += 1
        if spike:
            alerts_sent += 1

        ts    = datetime.now().strftime('%H:%M:%S')
        d     = payload['device_id']
        zone  = payload['zone']
        if use_mic:
            reading = f"{payload['sound_db']} dB"
            kind    = 'ALERT-LOG' if spike else 'mic-ok  '
        else:
            reading = f"{payload['temperature_c']} C"
            kind    = 'ALERT-FIRE' if spike else 'flame-ok'

        flag = '🚨' if spike else '  '
        print(f'{ts} {flag} {kind}  {d:<12}  {zone:<14}  {reading}  [r:{reads} a:{alerts_sent}]')

        time.sleep(INTERVAL)

    print(f'
[SIM] Stopped. Total readings: {reads} | Alerts: {alerts_sent}')
    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
