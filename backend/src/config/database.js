// Database configuration and connection pool
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://localhost/smartforest'
});

module.exports = {
  query: (text, params) => pool.query(text, params),
  execute: (text, params) => pool.query(text, params),
  pool
};
