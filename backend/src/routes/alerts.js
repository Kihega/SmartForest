const express    = require('express');
const router     = express.Router();
const alertModel = require('../models/alertModel');

// GET /api/alerts — all alerts newest first
router.get('/', async (req, res) => {
  try {
    const alerts = await alertModel.getAll();
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/alerts/count — unresolved alert count (for navbar badge)
router.get('/count', async (req, res) => {
  try {
    const count = await alertModel.countUnresolved();
    res.json({ count });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/alerts/unresolved — only unresolved alerts
router.get('/unresolved', async (req, res) => {
  try {
    const alerts = await alertModel.getUnresolved();
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/alerts/:id — single alert
router.get('/:id', async (req, res) => {
  try {
    const alert = await alertModel.getById(req.params.id);
    if (!alert) return res.status(404).json({ error: 'Alert not found' });
    res.json(alert);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/alerts/:id/resolve — mark alert as resolved
router.patch('/:id/resolve', async (req, res) => {
  try {
    const alert = await alertModel.resolve(req.params.id);
    if (!alert) return res.status(404).json({ error: 'Alert not found' });
    res.json({ message: 'Alert resolved', alert });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
