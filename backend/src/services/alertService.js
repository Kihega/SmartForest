const alertModel  = require('../models/alertModel');
require('dotenv').config();

const SOUND_THRESHOLD     = parseFloat(process.env.SOUND_THRESHOLD_DB || 80);
const VIBRATION_THRESHOLD = parseFloat(process.env.VIBRATION_THRESHOLD || 7);
const DEDUP_MINUTES       = 5; // suppress duplicate alerts within 5 minutes

const alertService = {

  // Evaluate a sensor reading and create an alert if thresholds exceeded
  async evaluateReading(data) {
    const { device_id, sound_db, vibration } = data;

    const isAlert = sound_db     > SOUND_THRESHOLD ||
                    vibration    > VIBRATION_THRESHOLD;

    if (!isAlert) return null;

    // Deduplication: skip if same device alerted recently
    const duplicate = await alertModel.recentlyAlerted(
      device_id, DEDUP_MINUTES
    );

    if (duplicate) {
      console.log(`[AlertService] Duplicate suppressed for ${device_id}`);
      return null;
    }

    // Create the alert
    const alert = await alertModel.create(data);
    console.log(`[AlertService] ALERT created: ${device_id} | zone: ${data.zone} | sound: ${sound_db}dB`);
    return alert;
  },

};

module.exports = alertService;
