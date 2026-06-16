'use strict';
const prisma = require('../config/prisma');
const pool   = require('../config/db');

function toSnake(u) {
  if (!u) return null;
  return {
    id:         u.id,
    name:       u.name,
    email:      u.email,
    role:       u.role,
    created_at: u.createdAt || u.created_at,
  };
}

const userModel = {
  async getByEmail(email) {
    try {
      return toSnake(await prisma.user.findUnique({ where: { email } }));
    } catch (e) {
      console.warn('[userModel] Prisma.getByEmail fallback:', e.message);
      const r = await pool.query('SELECT * FROM users WHERE email=$1', [email]);
      return r.rows[0] || null;
    }
  },

  async getById(id) {
    try {
      return toSnake(await prisma.user.findUnique({ where: { id: Number(id) } }));
    } catch (e) {
      console.warn('[userModel] Prisma.getById fallback:', e.message);
      const r = await pool.query('SELECT * FROM users WHERE id=$1', [id]);
      return r.rows[0] || null;
    }
  },

  async getAll() {
    try {
      const rows = await prisma.user.findMany({ orderBy: { createdAt: 'desc' } });
      return rows.map(toSnake);
    } catch (e) {
      console.warn('[userModel] Prisma.getAll fallback:', e.message);
      const r = await pool.query('SELECT * FROM users ORDER BY created_at DESC');
      return r.rows;
    }
  },

  // phone intentionally excluded — not in users table yet.
  // phone is stored in Supabase user_metadata (auth layer).
  async create({ name, email, role }) {
    try {
      return toSnake(await prisma.user.upsert({
        where:  { email },
        update: { name: name || undefined },
        create: { name, email, role: role || 'customer' },
      }));
    } catch (e) {
      console.warn('[userModel] Prisma.create fallback:', e.message);
      const r = await pool.query(
        \`INSERT INTO users (name, email, role)
         VALUES (\$1,\$2,\$3)
         ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
         RETURNING *\`,
        [name, email, role || 'customer']
      );
      return r.rows[0];
    }
  },

  async updateRole(id, role) {
    try {
      return toSnake(await prisma.user.update({
        where: { id: Number(id) },
        data:  { role },
      }));
    } catch (e) {
      console.warn('[userModel] Prisma.updateRole fallback:', e.message);
      const r = await pool.query(
        'UPDATE users SET role=\$1 WHERE id=\$2 RETURNING *', [role, id]
      );
      return r.rows[0] || null;
    }
  },

  async delete(id) {
    try {
      await prisma.user.delete({ where: { id: Number(id) } });
    } catch (e) {
      console.warn('[userModel] Prisma.delete fallback:', e.message);
      await pool.query('DELETE FROM users WHERE id=\$1', [id]);
    }
  },
};

module.exports = userModel;
