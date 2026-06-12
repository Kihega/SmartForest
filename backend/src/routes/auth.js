const express = require('express');
const router  = express.Router();

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'email and password are required' });
  }
  try {
    // TODO: const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    // if (error) return res.status(401).json({ error: error.message });
    // res.json({ token: data.session.access_token, user: data.user });
    res.status(401).json({ error: 'Invalid credentials' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/auth/logout
router.post('/logout', async (req, res) => {
  try {
    // TODO: await supabase.auth.signOut();
    res.json({ message: 'logged out' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
