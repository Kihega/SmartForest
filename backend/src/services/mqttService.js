const mqtt         = require('mqtt');
const sensorModel  = require('../models/sensorModel');
const alertService = require('./alertService');
require('dotenv').config();

const BROKER_URL = process.env.MQTT_BROKER || 'mqtt://localhost:1883';
const TOPIC      = process.env.MQTT_TOPIC  || 'forest/sensor/data';

function connectMQTT() {
  const client = mqtt.connect(BROKER_URL);

  client.on('connect', () => {
    client.subscribe(TOPIC);
    console.log(`[MQTT] Connected -> subscribed to: ${TOPIC}`);
  });

  client.on('message', async (topic, message) => {
    try {
      const data = JSON.parse(message.toString());

      // 1. Save every reading to sensor_readings table
      const reading = await sensorModel.saveReading(data);
      console.log(`[MQTT] Saved reading: ${data.device_id} | ${data.zone} | sound: ${data.sound_db}dB`);

      // 2. Check thresholds and create alert if needed
      await alertService.evaluateReading(data);

    } catch (err) {
      console.error(`[MQTT] Error processing message: ${err.message}`);
    }
  });

  client.on('error', (err) => {
    console.error(`[MQTT] Connection error: ${err.message}`);
  });

  client.on('reconnect', () => {
    console.log('[MQTT] Reconnecting...');
  });
}

module.exports = { connectMQTT };
