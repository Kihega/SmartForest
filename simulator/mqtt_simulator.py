#!/usr/bin/env python3
#
# SmartForest MQTT IoT Simulator
# Publishes fake sensor readings to test the full pipeline:
#   Simulator -> MQTT Broker -> Backend -> Supabase DB
#
# Usage:
#   source venv/bin/activate
#   python mqtt_simulator.py
#
# Env vars (optional overrides):
#   MQTT_BROKER_HOST  default: localhost
#   MQTT_BROKER_PORT  default: 1883
#   MQTT_TOPIC        default: forest/sensor/data
#   SEND_INTERVAL     default: 5 (seconds between readings)
#   SPIKE_CHANCE      default: 0.20 (20% chance of alert-level reading)

import paho.mqtt.client as mqtt
import json, random, time, os, sys
from datetime import datetime, timezone

BROKER   = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT     = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC    = os.getenv('MQTT_TOPIC', 'forest/sensor/data')
INTERVAL = float(os.getenv('SEND_INTERVAL', 5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE', 0.20))

ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
]

# ── MQTT callbacks ──────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'[MQTT] Connected to broker at {BROKER}:{PORT}')
    else:
        print(f'[MQTT] Connection failed, reason code: {reason_code}')
        sys.exit(1)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f'[MQTT] Unexpected disconnect ({reason_code}) - will retry...')

def on_publish(client, userdata, mid, reason_code, properties):
    pass  # successful publish confirmed

# ── Setup client ────────────────────────────────────────
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_publish    = on_publish

print(f'[SIM] Connecting to mqtt://{BROKER}:{PORT} ...')
try:
    client.connect(BROKER, PORT, keepalive=60)
except Exception as e:
    print(f'[SIM] ERROR: Cannot connect to broker -> {e}')
    print('[SIM] Make sure Mosquitto is running:')
    print('      sudo apt install mosquitto -y')
    print('      mosquitto -c mosquitto.conf')
    sys.exit(1)

client.loop_start()  # non-blocking loop for reconnects
time.sleep(1)        # wait for on_connect to fire

print(f'[SIM] Publishing to topic: {TOPIC}')
print(f'[SIM] Interval: {INTERVAL}s | Spike chance: {int(SPIKE_CHANCE*100)}%')
print(f'[SIM] Press Ctrl+C to stop\n')

reading_count = 0
alert_count   = 0

try:
    while True:
        zone  = random.choice(ZONES)
        spike = random.random() < SPIKE_CHANCE

        payload = {
            'device_id' : f"SENSOR-{random.randint(1, 5):03d}",
            'timestamp' : datetime.now(timezone.utc).isoformat(),
            'zone'      : zone['zone'],
            'latitude'  : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
            'longitude' : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
            'sound_db'  : round(random.uniform(82, 98) if spike
                                else random.uniform(20, 60), 2),
            'vibration' : round(random.uniform(7.5, 10) if spike
                                else random.uniform(0, 5), 2),
        }

        result = client.publish(TOPIC, json.dumps(payload))
        reading_count += 1
        if spike:
            alert_count += 1

        ts  = datetime.now().strftime('%H:%M:%S')
        tag = '[ALERT]' if spike else '[  ok ]'
        print(
            f"{ts} {tag} "
            f"{payload['device_id']} | "
            f"{payload['zone']} | "
            f"Sound: {payload['sound_db']} dB | "
            f"Vib: {payload['vibration']} | "
            f"readings: {reading_count} alerts: {alert_count}"
        )

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print(f'\n[SIM] Stopped. Total readings: {reading_count}, alerts: {alert_count}')
    client.loop_stop()
    client.disconnect()
