const mqtt = require('mqtt');
require('dotenv').config();

const BROKER_URL          = process.env.MQTT_BROKER || 'mqtt://localhost:1883';
const TOPIC               = process.env.MQTT_TOPIC  || 'forest/sensor/data';
const SOUND_THRESHOLD     = parseFloat(process.env.SOUND_THRESHOLD_DB || 80);
const VIBRATION_THRESHOLD = parseFloat(process.env.VIBRATION_THRESHOLD || 7);

function connectMQTT() {
  const client = mqtt.connect(BROKER_URL);

  client.on('connect', () => {
    client.subscribe(TOPIC);
    console.log(`MQTT connected — subscribed to: ${TOPIC}`);
  });

  client.on('message', async (topic, message) => {
    try {
      const data    = JSON.parse(message.toString());
      const isAlert = data.sound_db > SOUND_THRESHOLD ||
                      data.vibration > VIBRATION_THRESHOLD;
      // TODO: call sensorModel.saveReading() and alertService.handleAlert()
      console.log(`Sensor: ${data.device_id} | Sound: ${data.sound_db}dB | Alert: ${isAlert}`);
    } catch (err) {
      console.error('MQTT message error:', err.message);
    }
  });

  client.on('error', (err) => {
    console.error('MQTT connection error:', err.message);
  });
}

module.exports = { connectMQTT };
