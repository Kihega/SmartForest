const express      = require('express');
const cors         = require('cors');
const dotenv       = require('dotenv');
const { connectMQTT } = require('./services/mqttService');
const errorHandler = require('./middleware/errorHandler');

dotenv.config();

const app  = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/alerts',  require('./routes/alerts'));
app.use('/api/sensors', require('./routes/sensors'));
app.use('/api/auth',    require('./routes/auth'));
app.use('/api/devices', require('./routes/devices'));
app.use('/api/admin',   require('./routes/admin'));

// Health check
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.use(errorHandler);

let server;
if (process.env.NODE_ENV !== 'test') {
  connectMQTT();
  server = app.listen(PORT, () => {
    console.log(`SmartForest backend running on http://localhost:${PORT}`);
  });
}

module.exports = { app, server };
