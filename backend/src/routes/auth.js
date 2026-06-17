
const express   = require('express');
const router    = express.Router();
const supabase  = require('../config/supabase');
const userModel = require('../models/userModel');

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({
      error : 'email and password are required',
      reason: 'missing_fields',
    });
  }

  let result;
  try {
    result = await supabase.auth.signInWithPassword({ email, password });
  } catch (networkErr) {
    // Supabase project unreachable, wrong URL, or service down —
    // this is DIFFERENT from a wrong password, and the user needs to
    // know it's not their fault.
    console.error('[auth] Supabase unreachable:', networkErr.message);
    return res.status(503).json({
      error : 'Cannot reach the authentication service right now. Please try again shortly.',
      reason: 'supabase_unreachable',
    });
  }

  const { data, error } = result;
  if (error) {
    // Log full detail server-side for debugging deploys; never leak
    // Supabase internals to the client beyond a safe, clear message.
    console.warn('[auth] Login rejected for', email, '-', error.message, '| status:', error.status);
    return res.status(401).json({
      error : 'Incorrect email or password.',
      reason: 'invalid_credentials',
    });
  }

  try {
    const profile = await userModel.create({
      name  : data.user.user_metadata?.name || email.split('@')[0],
      email : data.user.email,
      role  : data.user.user_metadata?.role || 'ranger',
    });

    res.json({
      token   : data.session.access_token,
      expires : data.session.expires_at,
      role    : profile.role,
      user    : {
        id    : data.user.id,
        email : data.user.email,
        role  : profile.role,
        name  : profile.name,
      }
    });
  } catch (dbErr) {
    // Auth succeeded but our own DB profile sync failed (e.g. Prisma
    // can't reach DATABASE_URL). Tell the truth instead of "login failed".
    console.error('[auth] Profile sync failed after successful auth:', dbErr.message);
    res.status(500).json({
      error : 'Signed in, but could not load your profile. Please try again.',
      reason: 'profile_sync_failed',
    });
  }
});

// POST /api/auth/register
router.post('/register', async (req, res) => {
  const { firstName, surName, email, phone, password } = req.body;
  if (!firstName || !email || !password) {
    return res.status(400).json({ error: 'firstName, email and password are required' });
  }
  if (password.length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters' });
  }
  try {
    const name = `${firstName} ${surName || ''}`.trim();
    const { data, error } = await supabase.auth.signUp({
      email, password,
      options: { data: { name, phone: phone || '', role: 'customer' } }
    });
    if (error) return res.status(400).json({ error: error.message, reason: 'signup_rejected' });

    await userModel.create({ name, email, role: 'customer' });
    res.status(201).json({ message: 'Account created. Please sign in.' });
  } catch (err) {
    console.error('[auth] Register error:', err.message);
    res.status(500).json({ error: err.message, reason: 'server_error' });
  }
});

// POST /api/auth/change-password
router.post('/change-password', async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token)          return res.status(401).json({ error: 'Not authenticated' });
  if (!newPassword || newPassword.length < 8)
    return res.status(400).json({ error: 'New password must be at least 8 characters' });

  try {
    const { data: userData, error: ue } = await supabase.auth.getUser(token);
    if (ue) return res.status(401).json({ error: 'Invalid session' });

    const { error: loginErr } = await supabase.auth.signInWithPassword({
      email: userData.user.email, password: currentPassword,
    });
    if (loginErr) return res.status(401).json({ error: 'Current password is incorrect' });

    const { error: updateErr } = await supabase.auth.updateUser({ password: newPassword });
    if (updateErr) return res.status(400).json({ error: updateErr.message });

    res.json({ message: 'Password updated successfully' });
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

// GET /api/auth/me
router.get('/me', async (req, res) => {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'No token provided' });
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
