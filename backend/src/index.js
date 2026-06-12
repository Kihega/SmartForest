const express  = require('express');
const cors     = require('cors');
const dotenv   = require('dotenv');
const { connectMQTT } = require('./services/mqttService');

dotenv.config();

const app  = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/alerts',  require('./routes/alerts'));
app.use('/api/sensors', require('./routes/sensors'));
app.use('/api/auth',    require('./routes/auth'));

// Health check — used by frontend to detect if backend is live
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start MQTT subscriber
connectMQTT();

app.listen(PORT, () => {
  console.log(`SmartForest backend running on http://localhost:${PORT}`);
});

module.exports = app;
