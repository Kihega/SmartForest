const express = require('express');
const router  = express.Router();

// GET /api/sensors — all readings
router.get('/', async (req, res) => {
  try {
    // TODO: const rows = await sensorModel.getAll();
    res.json([]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/sensors/live — latest reading per device
router.get('/live', async (req, res) => {
  try {
    // TODO: const rows = await sensorModel.getLive();
    res.json([]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/sensors — manual sensor data post
router.post('/', async (req, res) => {
  const { device_id, sound_db, vibration } = req.body;
  if (!device_id) {
    return res.status(400).json({ error: 'device_id is required' });
  }
  try {
    // TODO: await sensorModel.saveReading(req.body);
    res.status(201).json({ message: 'reading saved', data: req.body });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
