const express   = require('express');
const router    = express.Router();
const supabase  = require('../config/supabase');
const userModel = require('../models/userModel');

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'email and password are required' });
  }
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email, password
    });
    if (error) return res.status(401).json({ error: error.message });

    // Sync user profile to our users table
    const profile = await userModel.create({
      name  : data.user.user_metadata?.name || email.split('@')[0],
      email : data.user.email,
      role  : data.user.user_metadata?.role || 'ranger',
    });

    res.json({
      token   : data.session.access_token,
      expires : data.session.expires_at,
      user    : {
        id    : data.user.id,
        email : data.user.email,
        role  : profile.role,
        name  : profile.name,
      }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/auth/logout
router.post('/logout', async (req, res) => {
  try {
    await supabase.auth.signOut();
    res.json({ message: 'Logged out successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/auth/me — return current user from token
router.get('/me', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const { data, error } = await supabase.auth.getUser(token);
    if (error) return res.status(401).json({ error: error.message });
    const profile = await userModel.getByEmail(data.user.email);
    res.json({ user: { ...data.user, profile } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
