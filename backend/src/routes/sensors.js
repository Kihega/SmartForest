const express     = require('express');
const router      = express.Router();
const sensorModel = require('../models/sensorModel');

// GET /api/sensors — all readings (newest first, limit 100)
router.get('/', async (req, res) => {
  try {
    const rows = await sensorModel.getAll();
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/sensors/live — latest reading per device
router.get('/live', async (req, res) => {
  try {
    const rows = await sensorModel.getLive();
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/sensors/:device_id — readings for a specific device
router.get('/:device_id', async (req, res) => {
  try {
    const rows = await sensorModel.getByDevice(req.params.device_id);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/sensors — manual sensor data post (testing + fallback)
router.post('/', async (req, res) => {
  const { device_id } = req.body;
  if (!device_id) {
    return res.status(400).json({ error: 'device_id is required' });
  }
  try {
    const reading = await sensorModel.saveReading(req.body);
    res.status(201).json({ message: 'reading saved', data: reading });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
