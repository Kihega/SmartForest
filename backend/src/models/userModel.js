const pool = require('../config/db');

const userModel = {

  // Get user by email
  async getByEmail(email) {
    const result = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );
    return result.rows[0] || null;
  },

  // Get user by id
  async getById(id) {
    const result = await pool.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  },

  // Create new user profile (linked to Supabase Auth)
  async create(data) {
    const { name, email, role } = data;
    const result = await pool.query(
      `INSERT INTO users (name, email, role)
       VALUES ($1, $2, $3)
       ON CONFLICT (email) DO UPDATE
         SET name = EXCLUDED.name
       RETURNING *`,
      [name, email, role || 'ranger']
    );
    return result.rows[0];
  },

};

module.exports = userModel;
