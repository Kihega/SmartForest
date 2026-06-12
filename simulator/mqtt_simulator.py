# SmartForest MQTT IoT Simulator
# Simulates chainsaw-sound and vibration sensors in Kibiti forest zones.
#
# Run locally:  source venv/bin/activate && python mqtt_simulator.py
# Host on cloud: Railway.app or Render.com (see project-setup-summary.txt)

import paho.mqtt.client as mqtt
import json, random, time, os
from datetime import datetime, timezone

BROKER = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT   = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC  = os.getenv('MQTT_TOPIC', 'forest/sensor/data')

ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
]

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
print(f'Simulator started -> mqtt://{BROKER}:{PORT}/{TOPIC}')

while True:
    zone  = random.choice(ZONES)
    spike = random.random() < 0.20   # 20% chance = suspicious activity

    payload = {
        'device_id' : f"SENSOR-{random.randint(1, 5):03d}",
        'timestamp' : datetime.now(timezone.utc).isoformat(),
        'zone'      : zone['zone'],
        'latitude'  : zone['lat'] + random.uniform(-0.01, 0.01),
        'longitude' : zone['lng'] + random.uniform(-0.01, 0.01),
        'sound_db'  : round(random.uniform(82, 98) if spike else random.uniform(20, 60), 2),
        'vibration' : round(random.uniform(7.5, 10) if spike else random.uniform(0, 5), 2),
    }

    client.publish(TOPIC, json.dumps(payload))
    tag = 'ALERT ' if spike else 'normal'
    print(f"[{tag}] {payload['zone']} | Sound: {payload['sound_db']} dB | Vib: {payload['vibration']}")
    time.sleep(5)
