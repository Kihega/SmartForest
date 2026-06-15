const alertModel = require('../models/alertModel');
require('dotenv').config();

// Thresholds
const SOUND_THRESHOLD = parseFloat(process.env.SOUND_THRESHOLD_DB   || 80);  // dB
const TEMP_THRESHOLD  = parseFloat(process.env.TEMP_THRESHOLD_C     || 55);  // Celsius
const DEDUP_MINUTES   = parseInt(process.env.DEDUP_MINUTES          || 5);

const alertService = {

  async evaluateReading(data) {
    const { device_id, sensor_type } = data;

    let isAlert   = false;
    let alertType = null;

    if (sensor_type === 'microphone') {
      // Microphone: detects chainsaw noise = illegal logging
      isAlert   = data.sound_db > SOUND_THRESHOLD;
      alertType = 'illegal_logging';

    } else if (sensor_type === 'flame') {
      // Flame sensor: detects fire via flame flag OR high temperature
      isAlert   = data.flame_detected === true ||
                  data.temperature_c  > TEMP_THRESHOLD;
      alertType = 'fire';
    }

    if (!isAlert) return null;

    // Deduplication: suppress if same device alerted recently
    const duplicate = await alertModel.recentlyAlerted(
      device_id, DEDUP_MINUTES
    );
    if (duplicate) {
      console.log(`[AlertService] Suppressed duplicate: ${device_id} (${sensor_type})`);
      return null;
    }

    const alert = await alertModel.create({ ...data, alert_type: alertType });

    const detail = sensor_type === 'microphone'
      ? `sound: ${data.sound_db}dB (threshold: ${SOUND_THRESHOLD}dB)`
      : `flame: ${data.flame_detected} | temp: ${data.temperature_c}C (threshold: ${TEMP_THRESHOLD}C)`;

    console.log(`[AlertService] ${alertType.toUpperCase()} ALERT -> ${device_id} | ${data.zone} | ${detail}`);
    return alert;
  },

};

module.exports = alertService;
