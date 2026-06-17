const express      = require('express');
const cors         = require('cors');
const dotenv       = require('dotenv');
const { connectMQTT } = require('./services/mqttService');
const { startCleanupSchedule } = require('./services/cleanupService');
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

// Health check -- reports which Supabase project this deployment uses,
// plus the active sensor-data retention window.
app.get('/api/health', (_req, res) => {
  let supabaseRef = 'NOT_CONFIGURED';
  try {
    const url = process.env.SUPABASE_URL || '';
    const match = url.match(/https:\/\/([a-z0-9]+)\.supabase\.co/i);
    supabaseRef = match ? match[1] : (url ? 'UNRECOGNISED_URL_FORMAT' : 'NOT_SET');
  } catch (_) { /* ignore */ }

  res.json({
    status          : 'ok',
    timestamp       : new Date().toISOString(),
    supabaseProject : supabaseRef,
    nodeEnv         : process.env.NODE_ENV || 'development',
    hasServiceKey   : !!process.env.SUPABASE_SERVICE_KEY,
    hasDbUrl        : !!process.env.DATABASE_URL,
    sensorTtlMinutes: parseInt(process.env.SENSOR_TTL_MINUTES || '9', 10),
  });
});

app.use(errorHandler);

let server;
if (process.env.NODE_ENV !== 'test') {
  connectMQTT();
  startCleanupSchedule();   // begin the 9-minute sensor-data TTL sweep
  server = app.listen(PORT, () => {
    console.log(`SmartForest backend running on http://localhost:${PORT}`);
    console.log(`Supabase project: ${(process.env.SUPABASE_URL || 'NOT SET')}`);
  });
}

module.exports = { app, server };
