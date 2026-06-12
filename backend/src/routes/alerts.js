const express = require('express');
const router  = express.Router();

// GET /api/alerts — return all alerts
router.get('/', async (req, res) => {
  try {
    // TODO: replace with real DB query
    // const alerts = await alertModel.getAll();
    res.json([]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/alerts/:id — single alert
router.get('/:id', async (req, res) => {
  try {
    // TODO: const alert = await alertModel.getById(req.params.id);
    // if (!alert) return res.status(404).json({ error: 'Not found' });
    res.status(404).json({ error: 'Not found' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/alerts/:id/resolve — mark alert resolved
router.patch('/:id/resolve', async (req, res) => {
  try {
    // TODO: await alertModel.resolve(req.params.id)
    res.json({ message: 'resolved' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
