#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates real hardware sensor units. Sends a NEW reading every 3 minutes
# (180s) by default, with realistic parameter drift between readings so
# values change gradually rather than jumping randomly each time.
#
# Backend URL -- SINGLE env var, no priority list:
#   BACKEND_URL=http://localhost:5000        (local)
#   BACKEND_URL=https://your-app.onrender.com (cloud)
# Whichever one is set is what the simulator uses. No code change needed
# to switch between local and cloud -- just change .env and restart.
#
# Hardware ID convention:
#   Real hardware : smf-m01a (microphone), smf-f01a (flame)
#   Simulator     : smt-m01a (microphone), smt-f01a (flame)
#
# Usage:
#   pip install -r requirements.txt
#   python mqtt_simulator.py             # run with defaults (180s interval)
#   python mqtt_simulator.py --stop      # graceful stop
#   python mqtt_simulator.py --interval 30 --spike 0.3   # faster for testing
#   USE_REAL_IDS=true python mqtt_simulator.py
#
# Env vars (set in simulator/.env):
#   BACKEND_URL         single backend URL -- local or cloud, doesn't matter
#   MQTT_BROKER_HOST    default: localhost (optional -- HTTP works standalone)
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   SEND_INTERVAL       default: 180 (seconds -- 3 minutes, matches real HW)
#   SPIKE_CHANCE        default: 0.20
#   USE_REAL_IDS        default: false

import json, random, time, os, sys, argparse, signal, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# -- Optional MQTT (HTTP-only mode works fine without a broker) --------------
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

# -- Load .env if python-dotenv is available ----------------------------------
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f'[SIM] Loaded env: {env_file}')
except ImportError:
    pass

# -- Config: ONE backend URL, no fallback list --------------------------------
BACKEND_URL  = os.getenv('BACKEND_URL', 'http://localhost:5000').rstrip('/')
BROKER       = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC', 'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL', 180))   # 3 minutes, matches real HW
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE', 0.20))
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
SENTINEL = Path(__file__).resolve().parent / "STOP_SIMULATOR"

PREFIX    = 'smf' if USE_REAL_IDS else 'smt'
MIC_IDS   = [f'{PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_IDS = [f'{PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
    {'zone': 'Kibiti-West',  'lat': -7.80, 'lng': 38.82},
]

# -- Drifting state per device, so each new reading shifts gradually ---------
# instead of jumping randomly -- mimics real sensor behaviour over time.
_state = {}

def _drift(device_id, base, lo, hi, max_step):
    prev = _state.get(device_id, base)
    step = random.uniform(-max_step, max_step)
    val  = max(lo, min(hi, prev + step))
    _state[device_id] = val
    return round(val, 2)

# -- Backend health probe ------------------------------------------------------
def probe_backend(timeout=5):
    try:
        req = urllib.request.urlopen(BACKEND_URL + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception as e:
        print(f'[SIM] Backend probe failed: {e}')
        return False

# -- Payload generators (with gradual drift) ----------------------------------
def make_mic(spike):
    z = random.choice(ZONES)
    device = random.choice(MIC_IDS)
    if spike:
        db = round(random.uniform(82, 98), 2)
    else:
        db = _drift(device, 35, 18, 65, 6)
    return {
        'device_id'    : device,
        'sensor_type'  : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'    : datetime.now(timezone.utc).isoformat(),
        'zone'         : z['zone'],
        'latitude'     : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'    : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'     : db,
    }

def make_flame(spike):
    z = random.choice(ZONES)
    device = random.choice(FLAME_IDS)
    if spike:
        temp = round(random.uniform(58, 95), 2)
    else:
        temp = _drift(device, 27, 20, 42, 3)
    return {
        'device_id'      : device,
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : z['zone'],
        'latitude'       : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : bool(spike),
        'temperature_c'  : temp,
    }

# -- HTTP POST to backend ------------------------------------------------------
def post_reading(payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            BACKEND_URL + '/api/sensors',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=8)
        return True
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')
        return False

# -- MQTT callbacks (optional) -------------------------------------------------
_running = True

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print(f'[MQTT] Connected: {BROKER}:{PORT}  topic: {TOPIC}')
    else:
        print(f'[MQTT] Connect failed rc={rc}')

def on_disconnect(client, userdata, flags, rc, props=None):
    if rc != 0:
        print(f'[MQTT] Disconnected rc={rc} -- will retry on next publish')

def graceful_stop(sig, frame):
    global _running
    print('\\n[SIM] Stopping...')
    _running = False

# -- CLI -----------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Simulator')
    p.add_argument('--stop',      action='store_true', help='Stop a running instance')
    p.add_argument('--interval',  type=float, default=INTERVAL)
    p.add_argument('--spike',     type=float, default=SPIKE_CHANCE)
    p.add_argument('--real-hw',   action='store_true', help='Use smf-* IDs')
    p.add_argument('--http-only', action='store_true', help='Skip MQTT entirely')
    return p.parse_args()

# -- Main ------------------------------------------------------------------------
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
        PREFIX    = 'smf'
        MIC_IDS   = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_IDS = [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    if SENTINEL.exists():
        SENTINEL.unlink()

    hw_label = 'REAL HW' if USE_REAL_IDS else 'SIMULATOR'
    print('=' * 60)
    print('  SmartForest IoT Simulator')
    print('=' * 60)
    print(f'  Mode      : {hw_label}')
    print(f'  Backend   : {BACKEND_URL}   (single env var: BACKEND_URL)')
    print(f'  MIC IDs   : {MIC_IDS}')
    print(f'  FLAME IDs : {FLAME_IDS}')
    print(f'  Interval  : {INTERVAL}s ({INTERVAL/60:.1f} min)  |  Spike: {int(SPIKE_CHANCE*100)}%')
    print()

    if not probe_backend():
        print(f'[SIM] WARNING: backend not reachable at {BACKEND_URL}')
        print('[SIM] Will keep trying to POST each cycle -- check BACKEND_URL in .env')
    else:
        print(f'[SIM] Backend reachable: {BACKEND_URL}')

    client = None
    if HAS_MQTT and not args.http_only:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect    = on_connect
            client.on_disconnect = on_disconnect
            client.connect(BROKER, PORT, keepalive=60)
            client.loop_start()
            time.sleep(1.0)
        except Exception as e:
            print(f'[MQTT] Cannot connect: {e} -- continuing HTTP-only')
            client = None
    elif not HAS_MQTT:
        print('[SIM] paho-mqtt not installed -- running HTTP-only')

    print()
    print('  Ctrl+C  or  python mqtt_simulator.py --stop  to exit')
    print('-' * 60)

    reads = 0
    alerts_sent = 0

    while _running:
        if SENTINEL.exists():
            SENTINEL.unlink()
            print('[SIM] Stop sentinel detected -- exiting cleanly')
            break

        spike   = random.random() < SPIKE_CHANCE
        use_mic = reads % 2 == 0
        payload = make_mic(spike) if use_mic else make_flame(spike)

        if client:
            try:
                client.publish(TOPIC, json.dumps(payload))
            except Exception as e:
                print(f'  [MQTT] Publish failed: {e}')

        ok = post_reading(payload)

        reads += 1
        if spike:
            alerts_sent += 1

        ts   = datetime.now().strftime('%H:%M:%S')
        d    = payload['device_id']
        zone = payload['zone']
        if use_mic:
            reading = f"{payload['sound_db']} dB"
            kind    = 'ALERT-LOG' if spike else 'mic-ok  '
        else:
            reading = f"{payload['temperature_c']} C"
            kind    = 'ALERT-FIRE' if spike else 'flame-ok'

        flag   = '\U0001f6a8' if spike else '  '
        status = 'OK' if ok else 'FAIL'
        print(f'{ts} {flag} {kind}  {d:<12}  {zone:<14}  {reading:<10}  http:{status}  [r:{reads} a:{alerts_sent}]')

        time.sleep(INTERVAL)

    print(f'\\n[SIM] Stopped. Total readings: {reads} | Alerts: {alerts_sent}')
    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
