const pool = require('../config/db');

const userModel = {
  async getByEmail(email) {
    const result = await pool.query('SELECT * FROM users WHERE email=$1', [email]);
    return result.rows[0] || null;
  },
  async getById(id) {
    const result = await pool.query('SELECT * FROM users WHERE id=$1', [id]);
    return result.rows[0] || null;
  },
  async getAll() {
    const result = await pool.query('SELECT * FROM users ORDER BY created_at DESC');
    return result.rows;
  },
  async create(data) {
    const { name, email, role } = data;
    const result = await pool.query(
      `INSERT INTO users (name, email, role)
       VALUES ($1, $2, $3)
       ON CONFLICT (email) DO UPDATE
         SET name = EXCLUDED.name
       RETURNING *`,
      [name, email, role || 'customer']
    );
    return result.rows[0];
  },
  async updateRole(id, role) {
    const result = await pool.query(
      'UPDATE users SET role=$1 WHERE id=$2 RETURNING *', [role, id]
    );
    return result.rows[0] || null;
  },
  async delete(id) {
    await pool.query('DELETE FROM users WHERE id=$1', [id]);
  },
};

module.exports = userModel;
