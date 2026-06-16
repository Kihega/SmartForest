#!/usr/bin/env python3
"""
SmartForest — Comprehensive Patch Script
=========================================
Run from the repo root:  python smartforest_patch.py

What this script does:
  1. Rewrites frontend/src/pages/Login.jsx  — pixel-faithful to the design image
     (forest image carousel on left, artistic SMARTFOREST logo, sign-up popup)
  2. Rewrites frontend/src/pages/UserDashboard.jsx  — sidebar layout, live map,
     live alerts, devices management, change-password popup, dark/light mode,
     language translate stub, home & devices pages
  3. Rewrites frontend/src/pages/AdminDashboard.jsx — admin panel with user mgmt,
     device oversight, admin account management (never zero admins), system stats
  4. Rewrites frontend/src/components/Navbar.jsx — shared top-bar (logo + user info)
  5. Adds    frontend/src/components/Sidebar.jsx  — icon sidebar with all menu items
  6. Adds    frontend/src/components/ChangePasswordModal.jsx
  7. Adds    frontend/src/components/SignupModal.jsx  — with password strength checker
  8. Rewrites frontend/src/App.jsx  — dark-mode CSS variable injection
  9. Updates backend/src/routes/auth.js — adds /register and /change-password
 10. Adds    backend/src/routes/devices.js — register, list, delete, suspend device
 11. Adds    backend/src/routes/admin.js   — admin user management
 12. Updates backend/src/index.js  — mounts new routes
 13. Updates backend/src/models/userModel.js  — getAll, delete, updateRole
 14. Adds    database/migrations/004_create_devices.sql
 15. Adds    database/migrations/005_admin_seed.sql  — seeds first admin user
 16. Rewrites simulator/mqtt_simulator.py  — start/stop control, labeled as real HW
"""

import os, textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
# If run from outside the project, allow override via env var or first arg
import sys as _sys
if len(_sys.argv) > 1 and os.path.isdir(_sys.argv[1]):
    ROOT = os.path.abspath(_sys.argv[1])

def write(rel_path: str, content: str):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(textwrap.dedent(content).lstrip('\n'))
    print(f'  ✔  {rel_path}')

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOGIN PAGE  (pixel-faithful to design image)
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/pages/Login.jsx', r"""
import { useState, useEffect } from 'react'
import { getAPI } from '../services/api.js'
import SignupModal from '../components/SignupModal.jsx'

/* ── forest carousel images (place JPG/PNG files in src/assets/forest/) ──── */
const FOREST_IMGS = [
  '/assets/forest/forest1.jpg',
  '/assets/forest/forest2.jpg',
  '/assets/forest/forest3.jpg',
  '/assets/forest/forest4.jpg',
]

export default function Login({ onLogin }) {
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [imgIdx,   setImgIdx]   = useState(0)
  const [showPwd,  setShowPwd]  = useState(false)
  const [signup,   setSignup]   = useState(false)

  /* rotate carousel every 5 s */
  useEffect(() => {
    const t = setInterval(() => setImgIdx(i => (i + 1) % FOREST_IMGS.length), 5000)
    return () => clearInterval(t)
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const api = await getAPI()
      const res = await api.post('/auth/login', { email, password })
      onLogin(res.data)
    } catch (err) {
      setError(err?.response?.data?.error || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div style={css.page}>
        {/* ── top header bar ── */}
        <div style={css.header}>
          <div style={css.logoArea}>
            <div style={css.logoCircle}>
              <img
                src="/assets/logo.png"
                alt="SmartForest Logo"
                style={{ width:'100%', height:'100%', objectFit:'contain', borderRadius:'50%' }}
                onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='block' }}
              />
              <span style={{ display:'none', fontSize:12, color:'#4a7c59', textAlign:'center', lineHeight:1.2 }}>
                Image /<br/>Logo
              </span>
            </div>
            <ArtisticTitle />
          </div>
          <div style={css.headerLine} />
        </div>

        {/* ── main card ── */}
        <div style={css.card}>
          {/* left: forest image carousel */}
          <div style={css.forestSide}>
            <img
              key={imgIdx}
              src={FOREST_IMGS[imgIdx]}
              alt="Forest"
              style={css.forestImg}
              onError={e => {
                e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%23a8e6cf"/><stop offset="1" stop-color="%231a5c38"/></linearGradient></defs><rect width="400" height="500" fill="url(%23g)"/><text x="200" y="250" text-anchor="middle" font-size="16" fill="white" font-family="sans-serif">Place forest images in%0Apublic/assets/forest/</text></svg>'
              }}
            />
            {/* dot indicators */}
            <div style={css.dots}>
              {FOREST_IMGS.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setImgIdx(i)}
                  style={{ ...css.dot, ...(i === imgIdx ? css.dotActive : {}) }}
                  aria-label={`Image ${i + 1}`}
                />
              ))}
            </div>
          </div>

          {/* right: sign-in form */}
          <div style={css.formSide}>
            <div style={css.signInTitle}>
              <LeafIcon /> SIGN IN <LeafIcon flip />
            </div>
            <div style={css.signInLine} />

            {error && <div style={css.errBox} role="alert">{error}</div>}

            <form onSubmit={handleSubmit} noValidate>
              <label style={css.label} htmlFor="sf-email">Email</label>
              <div style={css.inputWrap}>
                <MailIcon />
                <input
                  id="sf-email"
                  data-testid="login-email"
                  style={css.input}
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              <label style={css.label} htmlFor="sf-password">Password</label>
              <div style={css.inputWrap}>
                <LockIcon />
                <input
                  id="sf-password"
                  data-testid="login-password"
                  style={css.input}
                  type={showPwd ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(v => !v)}
                  style={css.eyeBtn}
                  aria-label={showPwd ? 'Hide password' : 'Show password'}
                >
                  {showPwd ? '🙈' : '👁'}
                </button>
              </div>

              <button
                data-testid="login-submit"
                style={{ ...css.loginBtn, opacity: loading ? 0.7 : 1 }}
                type="submit"
                disabled={loading}
              >
                {loading ? 'Signing in…' : 'LOGIN'}
              </button>
            </form>

            <p style={css.signupRow}>
              Don&apos;t have an account?{' '}
              <button
                style={css.signupLink}
                onClick={() => setSignup(true)}
                data-testid="open-signup"
              >
                Sign up
              </button>
            </p>
          </div>
        </div>

        {/* ── footer ── */}
        <div style={css.footer}>
          <LeafIcon small /> &nbsp;© 2026 – SmartForest&nbsp; <LeafIcon small flip />
        </div>
      </div>

      {signup && (
        <SignupModal
          onClose={() => setSignup(false)}
          onSuccess={() => { setSignup(false); setError('Account created! Please sign in.') }}
        />
      )}
    </>
  )
}

/* ── Artistic SMARTFOREST SVG title ───────────────────────────────────────── */
function ArtisticTitle() {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:0 }}>
      <svg width="380" height="70" viewBox="0 0 380 70" style={{ overflow:'visible' }}>
        <defs>
          <linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"  stopColor="#5cb85c" />
            <stop offset="50%" stopColor="#3a9e3a" />
            <stop offset="100%" stopColor="#1f6b1f" />
          </linearGradient>
          <filter id="tf" x="-5%" y="-5%" width="110%" height="110%">
            <feDropShadow dx="1" dy="2" stdDeviation="1" floodColor="#1a4d1a" floodOpacity="0.5"/>
          </filter>
        </defs>
        <text
          x="0" y="58"
          fontFamily="'Georgia', serif"
          fontWeight="900"
          fontSize="60"
          fill="url(#tg)"
          stroke="#1f6b1f"
          strokeWidth="2"
          filter="url(#tf)"
          letterSpacing="2"
          style={{ fontStyle:'italic' }}
        >
          SmartForest
        </text>
        {/* decorative underline */}
        <path d="M0 64 Q190 74 380 64" stroke="#2e7d32" strokeWidth="3" fill="none" strokeLinecap="round"/>
      </svg>
    </div>
  )
}

/* ── tiny inline icons ────────────────────────────────────────────────────── */
function LeafIcon({ flip, small }) {
  const sz = small ? 14 : 18
  return (
    <svg width={sz} height={sz} viewBox="0 0 24 24" fill="#2e7d32"
      style={{ transform: flip ? 'scaleX(-1)' : 'none', display:'inline-block', verticalAlign:'middle' }}>
      <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 4-13 9 1.5-2 7-5 8-4z"/>
    </svg>
  )
}
function MailIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4a7c59" strokeWidth="2"
      style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)' }}>
      <rect x="2" y="4" width="20" height="16" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7"/>
    </svg>
  )
}
function LockIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4a7c59" strokeWidth="2"
      style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)' }}>
      <rect x="3" y="11" width="18" height="11" rx="2"/>
      <path d="M7 11V7a5 5 0 0110 0v4"/>
    </svg>
  )
}

/* ── styles ───────────────────────────────────────────────────────────────── */
const css = {
  page: {
    minHeight:'100vh',
    background:'linear-gradient(160deg,#e8f5e9 0%,#c8e6c9 40%,#a5d6a7 100%)',
    display:'flex', flexDirection:'column',
    alignItems:'center', justifyContent:'flex-start',
    padding:'0 16px 24px',
    fontFamily:"'Segoe UI', system-ui, sans-serif",
  },
  header: {
    width:'100%', maxWidth:860,
    paddingTop:24,
  },
  logoArea: {
    display:'flex', alignItems:'center', gap:16, marginBottom:8,
  },
  logoCircle: {
    width:72, height:72, borderRadius:'50%',
    border:'2px solid #4a7c59',
    display:'flex', alignItems:'center', justifyContent:'center',
    overflow:'hidden', background:'#f1f8f2', flexShrink:0,
  },
  headerLine: {
    height:3, background:'linear-gradient(90deg,#2e7d32,#81c784)',
    borderRadius:4, marginTop:4,
  },
  card: {
    display:'flex', width:'100%', maxWidth:860,
    background:'#fff', borderRadius:16,
    boxShadow:'0 8px 40px rgba(0,80,0,0.13)',
    overflow:'hidden', marginTop:24, minHeight:500,
  },
  forestSide: {
    flex:'0 0 42%', position:'relative', overflow:'hidden',
    background:'#1a5c38',
  },
  forestImg: {
    width:'100%', height:'100%', objectFit:'cover',
    display:'block',
    animation:'fadeIn .8s ease',
  },
  dots: {
    position:'absolute', bottom:12, left:'50%',
    transform:'translateX(-50%)',
    display:'flex', gap:6,
  },
  dot: {
    width:8, height:8, borderRadius:'50%',
    background:'rgba(255,255,255,0.5)', border:'none', cursor:'pointer', padding:0,
  },
  dotActive: { background:'#fff' },
  formSide: {
    flex:1, padding:'40px 44px',
    display:'flex', flexDirection:'column', justifyContent:'center',
  },
  signInTitle: {
    fontSize:26, fontWeight:800, color:'#1b5e20',
    textAlign:'center', letterSpacing:4, display:'flex',
    alignItems:'center', justifyContent:'center', gap:10,
    marginBottom:6,
  },
  signInLine: {
    height:2, background:'linear-gradient(90deg,transparent,#4caf50,transparent)',
    marginBottom:28,
  },
  label: {
    display:'block', fontSize:14, fontWeight:600,
    color:'#2e4a2e', marginBottom:6, marginTop:16,
  },
  inputWrap: {
    position:'relative', display:'flex', alignItems:'center',
  },
  input: {
    width:'100%', padding:'11px 40px 11px 40px',
    fontSize:14, border:'1.5px solid #c8e6c9',
    borderRadius:8, outline:'none',
    background:'#f9fef9', color:'#1b5e20',
    transition:'border-color .2s',
  },
  eyeBtn: {
    position:'absolute', right:10, background:'none',
    border:'none', cursor:'pointer', fontSize:16, padding:4,
    color:'#4a7c59',
  },
  loginBtn: {
    width:'100%', marginTop:28, padding:14,
    fontSize:15, fontWeight:800, letterSpacing:2,
    background:'#2e7d32', color:'#fff',
    border:'none', borderRadius:8, cursor:'pointer',
    transition:'background .2s',
  },
  errBox: {
    background:'#ffebee', color:'#c62828',
    borderRadius:8, padding:'10px 14px',
    fontSize:13, marginBottom:4, border:'1px solid #ffcdd2',
  },
  signupRow: {
    textAlign:'center', marginTop:18, fontSize:14, color:'#555',
  },
  signupLink: {
    background:'none', border:'none', cursor:'pointer',
    color:'#2e7d32', fontWeight:700, fontSize:14, textDecoration:'underline',
  },
  footer: {
    marginTop:20, fontSize:13, color:'#2e7d32',
    display:'flex', alignItems:'center', gap:4,
  },
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 2. SIGNUP MODAL
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/components/SignupModal.jsx', r"""
import { useState } from 'react'
import { getAPI } from '../services/api.js'

function strengthLabel(pwd) {
  if (!pwd) return { label:'', color:'#ccc', pct:0 }
  let s = 0
  if (pwd.length >= 8) s++
  if (/[A-Z]/.test(pwd)) s++
  if (/[0-9]/.test(pwd)) s++
  if (/[^A-Za-z0-9]/.test(pwd)) s++
  const map = [
    { label:'Too short', color:'#ef5350', pct:10 },
    { label:'Weak',      color:'#ff7043', pct:30 },
    { label:'Fair',      color:'#ffa726', pct:55 },
    { label:'Good',      color:'#66bb6a', pct:78 },
    { label:'Strong',    color:'#2e7d32', pct:100 },
  ]
  return map[s] || map[0]
}

export default function SignupModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    firstName:'', surName:'', email:'',
    phone:'', password:'', confirm:'',
  })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const strength = strengthLabel(form.password)

  function set(k) { return e => setForm(f => ({ ...f, [k]: e.target.value })) }

  async function submit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const api = await getAPI()
      await api.post('/auth/register', {
        firstName: form.firstName,
        surName:   form.surName,
        email:     form.email,
        phone:     form.phone,
        password:  form.password,
      })
      onSuccess()
    } catch (err) {
      setError(err?.response?.data?.error || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={ov} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={card}>
        <div style={header}>
          <span style={{ fontWeight:800, fontSize:18, color:'#1b5e20' }}>Create Account</span>
          <button style={closeBtn} onClick={onClose} aria-label="Close">✕</button>
        </div>

        {error && <div style={errBox} role="alert">{error}</div>}

        <form onSubmit={submit} noValidate style={{ display:'grid', gap:12 }}>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
            <Field label="First Name" id="su-fn" value={form.firstName} onChange={set('firstName')} required />
            <Field label="Surname"    id="su-sn" value={form.surName}   onChange={set('surName')}   required />
          </div>
          <Field label="Email"        id="su-em" type="email"   value={form.email}    onChange={set('email')}    required />
          <Field label="Phone Number" id="su-ph" type="tel"     value={form.phone}    onChange={set('phone')} />
          <Field label="Password"     id="su-pw" type="password" value={form.password} onChange={set('password')} required />

          {/* strength bar */}
          {form.password && (
            <div>
              <div style={{ height:4, background:'#e0e0e0', borderRadius:4, overflow:'hidden' }}>
                <div style={{ width:`${strength.pct}%`, height:'100%', background:strength.color,
                  borderRadius:4, transition:'width .3s, background .3s' }} />
              </div>
              <span style={{ fontSize:11, color:strength.color, fontWeight:600 }}>{strength.label}</span>
            </div>
          )}

          <Field label="Confirm Password" id="su-cp" type="password" value={form.confirm} onChange={set('confirm')} required />

          <button
            type="submit"
            data-testid="signup-submit"
            disabled={loading}
            style={{ ...submitBtn, opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Creating account…' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  )
}

function Field({ label, id, type='text', value, onChange, required }) {
  return (
    <div>
      <label htmlFor={id} style={{ display:'block', fontSize:13, fontWeight:600,
        color:'#2e4a2e', marginBottom:4 }}>
        {label}{required && <span style={{ color:'#c62828' }}> *</span>}
      </label>
      <input
        id={id}
        data-testid={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        style={{ width:'100%', padding:'9px 12px', fontSize:13,
          border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none',
          background:'#f9fef9', color:'#1b5e20' }}
      />
    </div>
  )
}

const ov = {
  position:'fixed', inset:0, background:'rgba(0,0,0,0.55)',
  display:'flex', alignItems:'center', justifyContent:'center',
  zIndex:1000, padding:16,
}
const card = {
  background:'#fff', borderRadius:14, padding:'28px 32px',
  width:'100%', maxWidth:480,
  boxShadow:'0 16px 48px rgba(0,60,0,0.18)',
  maxHeight:'90vh', overflowY:'auto',
}
const header = {
  display:'flex', justifyContent:'space-between',
  alignItems:'center', marginBottom:20,
}
const closeBtn = {
  background:'none', border:'none', fontSize:18,
  cursor:'pointer', color:'#555', lineHeight:1,
}
const errBox = {
  background:'#ffebee', color:'#c62828', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:12,
}
const submitBtn = {
  width:'100%', padding:12, fontSize:14,
  fontWeight:700, background:'#2e7d32', color:'#fff',
  border:'none', borderRadius:8, cursor:'pointer', marginTop:4,
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 3. CHANGE PASSWORD MODAL
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/components/ChangePasswordModal.jsx', r"""
import { useState } from 'react'
import { getAPI } from '../services/api.js'

export default function ChangePasswordModal({ session, onClose }) {
  const [current,  setCurrent]  = useState('')
  const [newPwd,   setNewPwd]   = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')
  const [loading,  setLoading]  = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError(''); setSuccess('')
    if (newPwd !== confirm) { setError('New passwords do not match.'); return }
    if (newPwd.length < 8)  { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      const api = await getAPI()
      await api.post('/auth/change-password',
        { currentPassword: current, newPassword: newPwd },
        { headers: { Authorization: `Bearer ${session.token}` } }
      )
      setSuccess('Password changed successfully!')
      setTimeout(onClose, 1500)
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to change password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={ov} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={card}>
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:20 }}>
          <span style={{ fontWeight:800, fontSize:17, color:'#1b5e20' }}>Change Password</span>
          <button style={closeBtn} onClick={onClose}>✕</button>
        </div>
        {error   && <div style={errBox}>{error}</div>}
        {success && <div style={okBox}>{success}</div>}
        <form onSubmit={submit} noValidate style={{ display:'grid', gap:14 }}>
          {[
            ['Current password', current, setCurrent, 'cp-cur'],
            ['New password',     newPwd,  setNewPwd,  'cp-new'],
            ['Confirm new',      confirm, setConfirm, 'cp-cnf'],
          ].map(([lbl, val, fn, id]) => (
            <div key={id}>
              <label htmlFor={id} style={lStyle}>{lbl}</label>
              <input id={id} data-testid={id} type="password" value={val}
                onChange={e => fn(e.target.value)} required
                style={iStyle} autoComplete="new-password" />
            </div>
          ))}
          <button type="submit" disabled={loading}
            style={{ ...subBtn, opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
const ov      = { position:'fixed', inset:0, background:'rgba(0,0,0,0.6)',
  display:'flex', alignItems:'center', justifyContent:'center', zIndex:1000 }
const card    = { background:'#fff', borderRadius:12, padding:'28px 32px',
  width:'100%', maxWidth:380, boxShadow:'0 12px 40px rgba(0,0,0,0.2)' }
const closeBtn= { background:'none', border:'none', fontSize:18, cursor:'pointer', color:'#555' }
const errBox  = { background:'#ffebee', color:'#c62828', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:8 }
const okBox   = { background:'#e8f5e9', color:'#1b5e20', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:8 }
const lStyle  = { display:'block', fontSize:13, fontWeight:600, color:'#2e4a2e', marginBottom:4 }
const iStyle  = { width:'100%', padding:'9px 12px', fontSize:13,
  border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }
const subBtn  = { width:'100%', padding:11, fontSize:14, fontWeight:700,
  background:'#2e7d32', color:'#fff', border:'none', borderRadius:8, cursor:'pointer' }
""")

# ─────────────────────────────────────────────────────────────────────────────
# 4. SHARED NAVBAR (top bar — same for both user & admin)
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/components/Navbar.jsx', r"""
/* Shared top-bar — appears identically in user & admin dashboards */
export default function Navbar({ session, alertCount, role }) {
  const user = session?.user || {}
  return (
    <nav style={nav}>
      {/* left: logo + title */}
      <div style={left}>
        <div style={logoCircle}>
          <img src="/assets/logo.png" alt="Logo"
            style={{ width:'100%', height:'100%', objectFit:'contain', borderRadius:'50%' }}
            onError={e => { e.target.style.display='none' }} />
        </div>
        <ArtTitle />
        <span style={roleTag}>{role === 'admin' ? '⚙ Admin' : '👤 User'}</span>
      </div>
      {/* right: alert badge + user name */}
      <div style={right}>
        {alertCount > 0 && (
          <span style={alertBadge}>🚨 {alertCount} alert{alertCount !== 1 ? 's' : ''}</span>
        )}
        <span style={userLabel}>{user.name || user.email || 'User'}</span>
      </div>
    </nav>
  )
}

function ArtTitle() {
  return (
    <svg width="180" height="34" viewBox="0 0 180 34">
      <defs>
        <linearGradient id="ntg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#81c784"/>
          <stop offset="100%" stopColor="#2e7d32"/>
        </linearGradient>
      </defs>
      <text x="0" y="28" fontFamily="Georgia, serif" fontWeight="900"
        fontSize="28" fill="url(#ntg)" stroke="#1b5e20" strokeWidth="0.5"
        style={{ fontStyle:'italic' }}>
        SmartForest
      </text>
    </svg>
  )
}

const nav = {
  background:'linear-gradient(90deg,#1b5e20,#2e7d32)',
  color:'#fff', display:'flex', alignItems:'center',
  justifyContent:'space-between', padding:'0 20px',
  height:56, boxShadow:'0 2px 10px rgba(0,0,0,0.25)',
  position:'sticky', top:0, zIndex:100,
}
const left       = { display:'flex', alignItems:'center', gap:12 }
const right      = { display:'flex', alignItems:'center', gap:14 }
const logoCircle = { width:36, height:36, borderRadius:'50%',
  border:'2px solid rgba(255,255,255,0.5)', overflow:'hidden',
  background:'rgba(255,255,255,0.15)', flexShrink:0 }
const roleTag    = { background:'rgba(255,255,255,0.18)', borderRadius:20,
  padding:'3px 10px', fontSize:11, fontWeight:700, letterSpacing:0.5 }
const alertBadge = { background:'#e53935', color:'#fff',
  borderRadius:20, padding:'3px 10px', fontSize:12, fontWeight:700 }
const userLabel  = { fontSize:13, opacity:0.9 }
""")

# ─────────────────────────────────────────────────────────────────────────────
# 5. SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/components/Sidebar.jsx', r"""
import { useState } from 'react'

const LANGS = ['English','Swahili','French','Portuguese','Arabic']

export default function Sidebar({ active, onNav, onLogout, mode, onModeChange, lang, onLangChange }) {
  const [modeOpen, setModeOpen] = useState(false)
  const [langOpen,  setLangOpen]  = useState(false)

  const items = [
    { id:'home',    icon:'🏠', label:'Home' },
    { id:'devices', icon:'📡', label:'Devices' },
  ]

  return (
    <aside style={{ ...sb, background: mode==='dark' ? '#1a2a1a' : '#1b5e20' }}>
      {items.map(it => (
        <SBBtn key={it.id} icon={it.icon} label={it.label}
          active={active===it.id} onClick={() => onNav(it.id)} />
      ))}

      {/* change password */}
      <SBBtn icon="🔑" label="Password" onClick={() => onNav('changepassword')} />

      {/* mode toggle */}
      <div style={{ position:'relative' }}>
        <SBBtn icon={mode==='dark' ? '🌙':'☀️'} label="Mode"
          onClick={() => setModeOpen(v => !v)} />
        {modeOpen && (
          <div style={dropdown}>
            {['light','dark'].map(m => (
              <button key={m} style={{ ...ddItem, fontWeight: mode===m ? 700 : 400 }}
                onClick={() => { onModeChange(m); setModeOpen(false) }}>
                {m === 'light' ? '☀️ Light' : '🌙 Dark'}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* translate */}
      <div style={{ position:'relative' }}>
        <SBBtn icon="🌐" label="Language" onClick={() => setLangOpen(v => !v)} />
        {langOpen && (
          <div style={dropdown}>
            {LANGS.map(l => (
              <button key={l} style={{ ...ddItem, fontWeight: lang===l ? 700 : 400 }}
                onClick={() => { onLangChange(l); setLangOpen(false) }}>
                {l}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* logout — pushed to bottom */}
      <div style={{ marginTop:'auto' }}>
        <SBBtn icon="🚪" label="Logout" onClick={onLogout} danger />
      </div>
    </aside>
  )
}

function SBBtn({ icon, label, active, onClick, danger }) {
  const [hover, setHover] = useState(false)
  return (
    <button
      title={label}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display:'flex', flexDirection:'column', alignItems:'center',
        justifyContent:'center', gap:4,
        width:60, padding:'12px 0',
        background: active
          ? 'rgba(255,255,255,0.25)'
          : hover
            ? 'rgba(255,255,255,0.12)'
            : 'transparent',
        border:'none', cursor:'pointer',
        color: danger ? '#ff8a80' : '#fff',
        borderRadius:8, fontSize:20,
        transition:'background .15s',
      }}
    >
      <span>{icon}</span>
      <span style={{ fontSize:9, fontWeight:600, letterSpacing:0.4, opacity:0.85 }}>
        {label}
      </span>
    </button>
  )
}

const sb = {
  width:68, minHeight:'calc(100vh - 56px)',
  display:'flex', flexDirection:'column',
  alignItems:'center', gap:4, paddingTop:12, paddingBottom:12,
  boxShadow:'2px 0 8px rgba(0,0,0,0.15)',
  flexShrink:0,
}
const dropdown = {
  position:'absolute', left:72, top:0,
  background:'#fff', borderRadius:8, minWidth:130,
  boxShadow:'0 4px 20px rgba(0,0,0,0.18)',
  zIndex:200, overflow:'hidden',
}
const ddItem = {
  display:'block', width:'100%', padding:'10px 16px',
  background:'none', border:'none', cursor:'pointer',
  fontSize:13, color:'#1b5e20', textAlign:'left',
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 6. USER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/pages/UserDashboard.jsx', r"""
import { useState, useEffect, useRef, useCallback } from 'react'
import Navbar  from '../components/Navbar.jsx'
import Sidebar from '../components/Sidebar.jsx'
import ChangePasswordModal from '../components/ChangePasswordModal.jsx'
import { getAPI } from '../services/api.js'

/* ── Leaflet map (OpenStreetMap — free, no API key needed) ─────────────────
   We use react-leaflet which is already in package.json.
   Google Maps would require: npm i @react-google-maps/api  and a paid API key.
   OpenStreetMap / Leaflet is the recommended free alternative.               */
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix leaflet default icon path issue with Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const alertIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="36"><ellipse cx="12" cy="30" rx="6" ry="3" fill="%23c00" opacity=".3"/><path d="M12 0C7.6 0 4 3.6 4 8c0 7 8 22 8 22s8-15 8-22c0-4.4-3.6-8-8-8z" fill="%23e53935"/><circle cx="12" cy="8" r="4" fill="white"/></svg>',
  iconSize:[24,36], iconAnchor:[12,36], popupAnchor:[0,-36],
})
const okIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="36"><ellipse cx="12" cy="30" rx="6" ry="3" fill="%23080" opacity=".3"/><path d="M12 0C7.6 0 4 3.6 4 8c0 7 8 22 8 22s8-15 8-22c0-4.4-3.6-8-8-8z" fill="%232e7d32"/><circle cx="12" cy="8" r="4" fill="white"/></svg>',
  iconSize:[24,36], iconAnchor:[12,36], popupAnchor:[0,-36],
})

const REFRESH_MS = 10_000

export default function UserDashboard({ session, onLogout }) {
  const [page,        setPage]        = useState('home')
  const [mode,        setMode]        = useState('light')
  const [lang,        setLang]        = useState('English')
  const [showPwdModal, setShowPwdModal] = useState(false)

  // data
  const [alerts,  setAlerts]  = useState([])
  const [sensors, setSensors] = useState([])
  const [devices, setDevices] = useState([])
  const [count,   setCount]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  const mountedRef = useRef(true)

  const load = useCallback(async () => {
    try {
      const api = await getAPI()
      const headers = { Authorization: `Bearer ${session.token}` }
      const [a, s, c, d] = await Promise.all([
        api.get('/alerts',        { headers }),
        api.get('/sensors/live',  { headers }),
        api.get('/alerts/count',  { headers }),
        api.get('/devices',       { headers }),
      ])
      if (!mountedRef.current) return
      setAlerts(a.data  || [])
      setSensors(s.data || [])
      setCount(c.data?.count || 0)
      setDevices(d.data || [])
      setError('')
    } catch {
      if (mountedRef.current) setError('Could not load data from backend.')
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [session.token])

  useEffect(() => {
    mountedRef.current = true
    load()
    const id = setInterval(load, REFRESH_MS)
    return () => { mountedRef.current = false; clearInterval(id) }
  }, [load])

  function handleNav(id) {
    if (id === 'changepassword') { setShowPwdModal(true); return }
    setPage(id)
  }

  /* apply dark mode CSS variables */
  useEffect(() => {
    const r = document.documentElement
    if (mode === 'dark') {
      r.style.setProperty('--bg',       '#121212')
      r.style.setProperty('--surface',  '#1e1e1e')
      r.style.setProperty('--text',     '#e0e0e0')
      r.style.setProperty('--sub',      '#9e9e9e')
      r.style.setProperty('--border',   '#333')
    } else {
      r.style.setProperty('--bg',       '#f1f8f2')
      r.style.setProperty('--surface',  '#ffffff')
      r.style.setProperty('--text',     '#1b2e1b')
      r.style.setProperty('--sub',      '#6b7280')
      r.style.setProperty('--border',   '#e5e7eb')
    }
  }, [mode])

  const bg      = mode === 'dark' ? '#121212' : '#f1f8f2'
  const surface = mode === 'dark' ? '#1e1e1e' : '#ffffff'
  const text    = mode === 'dark' ? '#e0e0e0' : '#1b2e1b'

  return (
    <div style={{ minHeight:'100vh', background:bg, color:text, fontFamily:"'Segoe UI',system-ui,sans-serif" }}>
      <Navbar session={session} alertCount={count} role="user" />

      <div style={{ display:'flex' }}>
        <Sidebar
          active={page} onNav={handleNav} onLogout={onLogout}
          mode={mode} onModeChange={setMode}
          lang={lang}  onLangChange={setLang}
        />

        <main style={{ flex:1, padding:'24px 28px', maxWidth:1200 }}>
          {error && <div style={errBanner}>{error}</div>}

          {page === 'home'    && <HomePage    alerts={alerts} sensors={sensors} count={count}
                                              loading={loading} surface={surface} text={text} />}
          {page === 'devices' && <DevicesPage devices={devices} alerts={alerts}
                                              session={session} onRefresh={load}
                                              loading={loading} surface={surface} text={text} />}
        </main>
      </div>

      {showPwdModal && (
        <ChangePasswordModal session={session} onClose={() => setShowPwdModal(false)} />
      )}
    </div>
  )
}

/* ── Home page content ────────────────────────────────────────────────────── */
function HomePage({ alerts, sensors, count, loading, surface, text }) {
  const recentAlerts = alerts.slice(0, 6)
  const mapCenter    = sensors.length
    ? [sensors[0].latitude || -7.78, sensors[0].longitude || 38.95]
    : [-7.78, 38.95]

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* stat cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:16 }}>
        {[
          { icon:'🚨', label:'Unresolved Alerts', val:count,         color:'#e53935' },
          { icon:'📡', label:'Active Sensors',    val:sensors.length, color:'#1b5e20' },
          { icon:'🔥', label:'Fire Alerts',
            val: alerts.filter(a=>a.alert_type==='fire').length,        color:'#f57c00' },
          { icon:'🪚', label:'Logging Alerts',
            val: alerts.filter(a=>a.alert_type==='illegal_logging').length, color:'#5c3317' },
        ].map(c => (
          <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
            <span style={{ fontSize:28 }}>{c.icon}</span>
            <span style={{ fontSize:12, opacity:0.7 }}>{c.label}</span>
            <span style={{ fontSize:28, fontWeight:800, color:c.color }}>
              {loading ? '…' : c.val}
            </span>
          </div>
        ))}
      </div>

      {/* live map */}
      <Section title="🗺 Live Device Map" surface={surface} text={text}>
        <div style={{ height:340, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {sensors.map(s => s.latitude && (
              <Marker key={s.id} position={[s.latitude, s.longitude]}
                icon={s.is_alert ? alertIcon : okIcon}>
                <Popup>
                  <strong>{s.device_id}</strong><br/>
                  Zone: {s.zone}<br/>
                  Status: {s.is_alert ? '🔴 Alert' : '🟢 Normal'}<br/>
                  {s.sensor_type === 'microphone'
                    ? `Sound: ${s.sound_db} dB`
                    : `Temp: ${s.temperature_c}°C`}
                </Popup>
                {s.is_alert && <Circle center={[s.latitude, s.longitude]}
                  radius={500} color="#e53935" fillOpacity={0.12} />}
              </Marker>
            ))}
          </MapContainer>
        </div>
        <p style={{ fontSize:11, color:'#888', marginTop:4 }}>
          Map: OpenStreetMap (free, no API key) · Red = alert · Green = normal
        </p>
      </Section>

      {/* live alert trends */}
      <Section title="⚡ Live Alert Trends" surface={surface} text={text}>
        {recentAlerts.length === 0
          ? <Empty>No alerts yet — all sensors reporting normal.</Empty>
          : (
            <div style={{ display:'grid', gap:8 }}>
              {recentAlerts.map(a => (
                <AlertRow key={a.id} alert={a} />
              ))}
              {alerts.length > 6 && (
                <p style={{ fontSize:12, color:'#888', textAlign:'right' }}>
                  Showing 6 of {alerts.length} alerts
                </p>
              )}
            </div>
          )}
      </Section>

      {/* system health summary */}
      <Section title="💚 System Health" surface={surface} text={text}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
          <HealthItem label="Microphone sensors" val={sensors.filter(s=>s.sensor_type==='microphone').length} />
          <HealthItem label="Flame sensors"      val={sensors.filter(s=>s.sensor_type==='flame').length} />
          <HealthItem label="Total alerts"       val={alerts.length} />
          <HealthItem label="Resolved"
            val={alerts.filter(a=>a.status==='resolved').length} good />
        </div>
      </Section>
    </div>
  )
}

/* ── Devices page ─────────────────────────────────────────────────────────── */
function DevicesPage({ devices, alerts, session, onRefresh, loading, surface, text }) {
  const [addId,    setAddId]    = useState('')
  const [addError, setAddError] = useState('')
  const [addOk,    setAddOk]    = useState('')
  const [busy,     setBusy]     = useState(false)

  const recentAlerts = alerts.slice(0, 6)

  async function addDevice(e) {
    e.preventDefault()
    setAddError(''); setAddOk('')
    if (!addId.trim()) { setAddError('Device ID is required.'); return }
    setBusy(true)
    try {
      const api = await getAPI()
      await api.post('/devices', { device_id: addId.trim() },
        { headers: { Authorization: `Bearer ${session.token}` } })
      setAddOk(`Device ${addId.trim()} registered successfully.`)
      setAddId('')
      onRefresh()
    } catch (err) {
      setAddError(err?.response?.data?.error || 'Failed to register device.')
    } finally {
      setBusy(false)
    }
  }

  async function removeDevice(id) {
    if (!confirm(`Delete device ${id}? This removes all related data.`)) return
    try {
      const api = await getAPI()
      await api.delete(`/devices/${id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Delete failed.')
    }
  }

  async function suspendDevice(id, active) {
    try {
      const api = await getAPI()
      await api.patch(`/devices/${id}/status`,
        { active: !active },
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Update failed.')
    }
  }

  const mapCenter = devices.length && devices[0].latitude
    ? [devices[0].latitude, devices[0].longitude]
    : [-7.78, 38.95]

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* live device map */}
      <Section title="🗺 Live Device Deployment" surface={surface} text={text}>
        <div style={{ height:300, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© OpenStreetMap contributors'/>
            {devices.map(d => d.latitude && (
              <Marker key={d.id} position={[d.latitude, d.longitude]}
                icon={d.active ? okIcon : alertIcon}>
                <Popup>
                  <strong>{d.device_id}</strong><br/>
                  Status: {d.active ? '🟢 Active' : '⭕ Suspended'}<br/>
                  Zone: {d.zone || '—'}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </Section>

      {/* live alerts */}
      <Section title="⚡ Recent Alerts" surface={surface} text={text}>
        {recentAlerts.length === 0
          ? <Empty>No alerts yet.</Empty>
          : recentAlerts.map(a => <AlertRow key={a.id} alert={a} />)}
      </Section>

      {/* add device */}
      <Section title="➕ Register New Device" surface={surface} text={text}>
        <p style={{ fontSize:13, color:'#666', marginBottom:12 }}>
          Enter the hardware ID printed on your device (e.g. <code>smf-01a</code> for real hardware
          or <code>smt-01a</code> for simulator units).
        </p>
        {addError && <div style={errBanner}>{addError}</div>}
        {addOk    && <div style={okBanner}>{addOk}</div>}
        <form onSubmit={addDevice} style={{ display:'flex', gap:10 }}>
          <input
            data-testid="device-id-input"
            placeholder="Device ID (e.g. smf-01a)"
            value={addId}
            onChange={e => setAddId(e.target.value)}
            style={{ flex:1, padding:'9px 12px', fontSize:13,
              border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }}
          />
          <button type="submit" disabled={busy}
            style={{ padding:'9px 20px', background:'#2e7d32', color:'#fff',
              border:'none', borderRadius:7, fontWeight:700, cursor:'pointer',
              opacity: busy ? 0.7 : 1 }}>
            {busy ? 'Adding…' : 'Add Device'}
          </button>
        </form>
      </Section>

      {/* registered devices list */}
      <Section title="📋 Registered Devices" surface={surface} text={text}>
        {loading
          ? <Empty>Loading…</Empty>
          : devices.length === 0
            ? <Empty>No devices registered yet. Add your first device above.</Empty>
            : (
              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
                <thead>
                  <tr>{['Device ID','Zone','Status','Last Seen','Actions'].map(h =>
                    <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {devices.map(d => (
                    <tr key={d.id}>
                      <td style={td}><strong>{d.device_id}</strong></td>
                      <td style={td}>{d.zone || '—'}</td>
                      <td style={td}>
                        <span style={d.active
                          ? { ...badge, background:'#e8f5e9', color:'#2e7d32' }
                          : { ...badge, background:'#fafafa', color:'#888' }}>
                          {d.active ? '🟢 Active' : '⭕ Suspended'}
                        </span>
                      </td>
                      <td style={{ ...td, color:'#888', fontSize:11 }}>
                        {d.last_seen ? new Date(d.last_seen).toLocaleString() : '—'}
                      </td>
                      <td style={td}>
                        <div style={{ display:'flex', gap:8 }}>
                          <button
                            title={d.active ? 'Suspend device (stops data stream)' : 'Resume device'}
                            onClick={() => suspendDevice(d.device_id, d.active)}
                            style={{ ...iconBtn, color: d.active ? '#f57c00' : '#2e7d32' }}>
                            {d.active ? '⏸' : '▶'}
                          </button>
                          <button
                            title="Delete device (removes all data)"
                            onClick={() => removeDevice(d.device_id)}
                            style={{ ...iconBtn, color:'#e53935' }}>
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
      </Section>
    </div>
  )
}

/* ── small shared components ─────────────────────────────────────────────── */
function Section({ title, children, surface, text }) {
  return (
    <div style={{ background:surface, borderRadius:12, padding:'20px 22px',
      boxShadow:'0 1px 6px rgba(0,0,0,0.08)', color:text }}>
      <div style={{ fontSize:15, fontWeight:700, marginBottom:14 }}>{title}</div>
      {children}
    </div>
  )
}

function AlertRow({ alert: a }) {
  const isLog = a.alert_type === 'illegal_logging'
  return (
    <div style={{ display:'flex', alignItems:'center', gap:12,
      padding:'10px 14px', borderRadius:8,
      background: isLog ? '#fff8e1' : '#ffebee',
      border:`1px solid ${isLog ? '#ffe082' : '#ffcdd2'}` }}>
      <span style={{ fontSize:22 }}>{isLog ? '🪚' : '🔥'}</span>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontWeight:700, fontSize:13 }}>
          {isLog ? 'Illegal Logging' : 'Fire Detected'} — {a.device_id}
        </div>
        <div style={{ fontSize:11, color:'#888' }}>
          {a.zone} · {a.sensor_type === 'microphone'
            ? `${a.sound_db} dB` : `${a.temperature_c}°C`}
        </div>
      </div>
      <div style={{ fontSize:11, color:'#aaa', whiteSpace:'nowrap' }}>
        {new Date(a.created_at).toLocaleString()}
      </div>
      <span style={{ ...badge,
        background: a.status==='resolved' ? '#e8f5e9' : '#ffebee',
        color:       a.status==='resolved' ? '#2e7d32' : '#c62828' }}>
        {a.status}
      </span>
    </div>
  )
}

function HealthItem({ label, val, good }) {
  return (
    <div style={{ padding:'12px 16px', borderRadius:8,
      background: good ? '#e8f5e9' : '#f5f5f5',
      display:'flex', justifyContent:'space-between', alignItems:'center' }}>
      <span style={{ fontSize:13, color:'#555' }}>{label}</span>
      <span style={{ fontSize:20, fontWeight:800, color: good ? '#2e7d32' : '#333' }}>{val}</span>
    </div>
  )
}

function Empty({ children }) {
  return <div style={{ textAlign:'center', padding:'32px', color:'#aaa', fontSize:13 }}>{children}</div>
}

/* ── style tokens ──────────────────────────────────────────────────────────  */
const statCard = { borderRadius:10, padding:'18px 16px',
  display:'flex', flexDirection:'column', gap:4,
  boxShadow:'0 1px 6px rgba(0,0,0,0.07)' }
const errBanner = { background:'#ffebee', color:'#c62828', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const okBanner  = { background:'#e8f5e9', color:'#1b5e20', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const th   = { textAlign:'left', padding:'8px 12px',
  background:'#f9fafb', color:'#6b7280', fontWeight:600,
  borderBottom:'1px solid #e5e7eb', fontSize:12 }
const td   = { padding:'10px 12px', borderBottom:'1px solid #f3f4f6', verticalAlign:'middle' }
const badge= { display:'inline-block', padding:'3px 9px',
  borderRadius:20, fontSize:11, fontWeight:600 }
const iconBtn = { background:'none', border:'none', cursor:'pointer',
  fontSize:18, padding:4, borderRadius:6 }
""")

# ─────────────────────────────────────────────────────────────────────────────
# 7. ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/pages/AdminDashboard.jsx', r"""
import { useState, useEffect, useRef, useCallback } from 'react'
import Navbar  from '../components/Navbar.jsx'
import Sidebar from '../components/Sidebar.jsx'
import ChangePasswordModal from '../components/ChangePasswordModal.jsx'
import { getAPI } from '../services/api.js'

export default function AdminDashboard({ session, onLogout }) {
  const [page,         setPage]         = useState('home')
  const [mode,         setMode]         = useState('light')
  const [lang,         setLang]         = useState('English')
  const [showPwdModal, setShowPwdModal] = useState(false)

  const [users,   setUsers]   = useState([])
  const [devices, setDevices] = useState([])
  const [alerts,  setAlerts]  = useState([])
  const [sensors, setSensors] = useState([])
  const [count,   setCount]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')
  const mountedRef = useRef(true)

  const load = useCallback(async () => {
    try {
      const api = await getAPI()
      const h = { headers: { Authorization: `Bearer ${session.token}` } }
      const [u, d, a, s, c] = await Promise.all([
        api.get('/admin/users',   h),
        api.get('/devices/all',   h),
        api.get('/alerts',        h),
        api.get('/sensors/live',  h),
        api.get('/alerts/count',  h),
      ])
      if (!mountedRef.current) return
      setUsers(u.data   || [])
      setDevices(d.data || [])
      setAlerts(a.data  || [])
      setSensors(s.data || [])
      setCount(c.data?.count || 0)
      setError('')
    } catch {
      if (mountedRef.current) setError('Could not load admin data.')
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [session.token])

  useEffect(() => {
    mountedRef.current = true
    load()
    const id = setInterval(load, 15_000)
    return () => { mountedRef.current = false; clearInterval(id) }
  }, [load])

  useEffect(() => {
    const r = document.documentElement
    if (mode === 'dark') {
      r.style.setProperty('--bg', '#121212')
      r.style.setProperty('--surface', '#1e1e1e')
      r.style.setProperty('--text', '#e0e0e0')
    } else {
      r.style.setProperty('--bg', '#f1f8f2')
      r.style.setProperty('--surface', '#ffffff')
      r.style.setProperty('--text', '#1b2e1b')
    }
  }, [mode])

  function handleNav(id) {
    if (id === 'changepassword') { setShowPwdModal(true); return }
    setPage(id)
  }

  const bg      = mode === 'dark' ? '#121212' : '#f1f8f2'
  const surface = mode === 'dark' ? '#1e1e1e' : '#ffffff'
  const text    = mode === 'dark' ? '#e0e0e0' : '#1b2e1b'

  const admins      = users.filter(u => u.role === 'admin')
  const adminCount  = admins.length
  const activeCount = devices.filter(d => d.active).length

  return (
    <div style={{ minHeight:'100vh', background:bg, color:text,
      fontFamily:"'Segoe UI',system-ui,sans-serif" }}>
      <Navbar session={session} alertCount={count} role="admin" />

      <div style={{ display:'flex' }}>
        <Sidebar
          active={page} onNav={handleNav} onLogout={onLogout}
          mode={mode} onModeChange={setMode}
          lang={lang}  onLangChange={setLang}
        />

        <main style={{ flex:1, padding:'24px 28px', maxWidth:1200 }}>
          {error && <div style={errBanner}>{error}</div>}

          {page === 'home' && (
            <AdminHome
              users={users} devices={devices} alerts={alerts} sensors={sensors}
              count={count} adminCount={adminCount} activeCount={activeCount}
              loading={loading} surface={surface} text={text}
              session={session} onRefresh={load}
            />
          )}
          {page === 'devices' && (
            <AdminDevices devices={devices} alerts={alerts}
              session={session} onRefresh={load} surface={surface} text={text} />
          )}
        </main>
      </div>

      {showPwdModal && (
        <ChangePasswordModal session={session} onClose={() => setShowPwdModal(false)} />
      )}
    </div>
  )
}

/* ── Admin Home ───────────────────────────────────────────────────────────── */
function AdminHome({ users, devices, alerts, sensors, count, adminCount,
  activeCount, loading, surface, text, session, onRefresh }) {

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* stat row */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(170px,1fr))', gap:16 }}>
        {[
          { icon:'👥', label:'Total Users',     val:users.length,   color:'#1b5e20' },
          { icon:'📡', label:'Total Devices',   val:devices.length, color:'#2563eb' },
          { icon:'🟢', label:'Active Devices',  val:activeCount,    color:'#2e7d32' },
          { icon:'🚨', label:'Open Alerts',     val:count,          color:'#e53935' },
          { icon:'⚙',  label:'Admin Accounts',  val:adminCount,     color:'#5c3317' },
        ].map(c => (
          <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
            <span style={{ fontSize:26 }}>{c.icon}</span>
            <span style={{ fontSize:11, opacity:0.7 }}>{c.label}</span>
            <span style={{ fontSize:26, fontWeight:800, color:c.color }}>
              {loading ? '…' : c.val}
            </span>
          </div>
        ))}
      </div>

      {/* User management */}
      <AdminUserTable users={users} session={session} onRefresh={onRefresh}
        surface={surface} text={text} />

      {/* Recent alerts overview */}
      <Section title="⚡ Recent System Alerts" surface={surface} text={text}>
        {alerts.slice(0, 8).length === 0
          ? <Empty>No alerts.</Empty>
          : alerts.slice(0, 8).map(a => (
            <div key={a.id} style={aRow}>
              <span style={{ fontSize:20 }}>{a.alert_type==='fire' ? '🔥' : '🪚'}</span>
              <div style={{ flex:1 }}>
                <strong style={{ fontSize:13 }}>{a.device_id}</strong>
                <span style={{ fontSize:11, color:'#888' }}> · {a.zone} · {new Date(a.created_at).toLocaleString()}</span>
              </div>
              <span style={{ ...badge,
                background: a.status==='resolved' ? '#e8f5e9' : '#ffebee',
                color:       a.status==='resolved' ? '#2e7d32' : '#c62828' }}>
                {a.status}
              </span>
            </div>
          ))}
      </Section>

      {/* Live sensors */}
      <Section title="📡 Live Sensor Readings" surface={surface} text={text}>
        {loading ? <Empty>Loading…</Empty> : sensors.length === 0
          ? <Empty>No sensor data. Start the simulator.</Empty>
          : (
            <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
              <thead><tr>
                {['Device','Type','Zone','Reading','Alert','Time'].map(h =>
                  <th key={h} style={th}>{h}</th>)}
              </tr></thead>
              <tbody>
                {sensors.map(s => (
                  <tr key={s.id}>
                    <td style={td}><strong>{s.device_id}</strong></td>
                    <td style={td}>{s.sensor_type === 'microphone' ? '🎙 Mic' : '🔥 Flame'}</td>
                    <td style={td}>{s.zone}</td>
                    <td style={td}>
                      {s.sensor_type === 'microphone'
                        ? `${s.sound_db} dB` : `${s.temperature_c}°C`}
                    </td>
                    <td style={td}>
                      <span style={s.is_alert
                        ? { ...badge, background:'#ffebee', color:'#c62828' }
                        : { ...badge, background:'#e8f5e9', color:'#2e7d32' }}>
                        {s.is_alert ? '🔴' : '🟢'}
                      </span>
                    </td>
                    <td style={{ ...td, fontSize:11, color:'#aaa' }}>
                      {new Date(s.recorded_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </Section>
    </div>
  )
}

/* ── Admin User Management table ──────────────────────────────────────────── */
function AdminUserTable({ users, session, onRefresh, surface, text }) {
  const [adding, setAdding] = useState(false)
  const [form,   setForm]   = useState({ name:'', email:'', password:'', role:'ranger' })
  const [error,  setError]  = useState('')
  const [ok,     setOk]     = useState('')

  const adminCount = users.filter(u => u.role === 'admin').length

  async function deleteUser(u) {
    if (u.role === 'admin' && adminCount <= 1) {
      alert('Cannot delete the last admin account.')
      return
    }
    if (!confirm(`Delete user ${u.email}?`)) return
    try {
      const api = await getAPI()
      await api.delete(`/admin/users/${u.id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Delete failed.')
    }
  }

  async function addAdmin(e) {
    e.preventDefault()
    setError(''); setOk('')
    try {
      const api = await getAPI()
      await api.post('/admin/users',
        { ...form, role:'admin' },
        { headers: { Authorization: `Bearer ${session.token}` } })
      setOk(`Admin ${form.email} created.`)
      setForm({ name:'', email:'', password:'', role:'ranger' })
      setAdding(false)
      onRefresh()
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to create admin.')
    }
  }

  return (
    <Section title="👥 User Management" surface={surface} text={text}>
      <div style={{ display:'flex', justifyContent:'flex-end', marginBottom:12 }}>
        <button onClick={() => setAdding(v => !v)}
          style={{ padding:'7px 16px', background:'#2e7d32', color:'#fff',
            border:'none', borderRadius:7, fontWeight:700, cursor:'pointer', fontSize:13 }}>
          {adding ? 'Cancel' : '+ Add Admin'}
        </button>
      </div>

      {adding && (
        <div style={{ background:'#f9fef9', border:'1px solid #c8e6c9',
          borderRadius:8, padding:16, marginBottom:16 }}>
          {error && <div style={errBanner}>{error}</div>}
          {ok    && <div style={okBanner}>{ok}</div>}
          <form onSubmit={addAdmin} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
            {[['Full Name','name','text'],['Email','email','email'],['Password','password','password']].map(
              ([lbl,k,t]) => (
                <div key={k}>
                  <label style={{ fontSize:12, fontWeight:600, display:'block', marginBottom:3 }}>{lbl}</label>
                  <input type={t} value={form[k]} onChange={e => setForm(f => ({ ...f, [k]:e.target.value }))}
                    required style={{ width:'100%', padding:'8px 10px', fontSize:13,
                      border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }} />
                </div>
              )
            )}
            <div style={{ gridColumn:'1/-1' }}>
              <button type="submit" style={{ padding:'8px 20px', background:'#1b5e20',
                color:'#fff', border:'none', borderRadius:7, fontWeight:700, cursor:'pointer' }}>
                Create Admin
              </button>
            </div>
          </form>
        </div>
      )}

      <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
        <thead><tr>
          {['Name','Email','Role','Joined','Actions'].map(h => <th key={h} style={th}>{h}</th>)}
        </tr></thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td style={td}>{u.name || '—'}</td>
              <td style={td}>{u.email}</td>
              <td style={td}>
                <span style={u.role === 'admin'
                  ? { ...badge, background:'#e8f5e9', color:'#1b5e20' }
                  : { ...badge, background:'#e3f2fd', color:'#1565c0' }}>
                  {u.role}
                </span>
              </td>
              <td style={{ ...td, fontSize:11, color:'#aaa' }}>
                {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
              </td>
              <td style={td}>
                <button
                  title={u.role==='admin' && adminCount<=1
                    ? 'Cannot delete last admin' : 'Delete user'}
                  onClick={() => deleteUser(u)}
                  disabled={u.id === session?.user?.id}
                  style={{ ...iconBtn, color:'#e53935',
                    opacity: u.id === session?.user?.id ? 0.3 : 1 }}>
                  🗑
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Section>
  )
}

/* ── Admin Devices page ───────────────────────────────────────────────────── */
function AdminDevices({ devices, alerts, session, onRefresh, surface, text }) {
  async function deleteDevice(id) {
    if (!confirm(`Delete device ${id}? All data will be removed.`)) return
    try {
      const api = await getAPI()
      await api.delete(`/devices/${id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Delete failed.')
    }
  }

  async function toggleDevice(id, active) {
    try {
      const api = await getAPI()
      await api.patch(`/devices/${id}/status`, { active: !active },
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Update failed.')
    }
  }

  return (
    <div style={{ display:'grid', gap:24 }}>
      <Section title="📡 All Devices" surface={surface} text={text}>
        {devices.length === 0
          ? <Empty>No devices in the system.</Empty>
          : (
            <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
              <thead><tr>
                {['Device ID','Owner','Zone','Status','Last Seen','Actions'].map(h =>
                  <th key={h} style={th}>{h}</th>)}
              </tr></thead>
              <tbody>
                {devices.map(d => (
                  <tr key={d.id}>
                    <td style={td}><strong>{d.device_id}</strong></td>
                    <td style={td}>{d.owner_email || '—'}</td>
                    <td style={td}>{d.zone || '—'}</td>
                    <td style={td}>
                      <span style={d.active
                        ? { ...badge, background:'#e8f5e9', color:'#2e7d32' }
                        : { ...badge, background:'#f5f5f5', color:'#888' }}>
                        {d.active ? '🟢 Active' : '⭕ Suspended'}
                      </span>
                    </td>
                    <td style={{ ...td, fontSize:11, color:'#aaa' }}>
                      {d.last_seen ? new Date(d.last_seen).toLocaleString() : '—'}
                    </td>
                    <td style={td}>
                      <div style={{ display:'flex', gap:8 }}>
                        <button onClick={() => toggleDevice(d.device_id, d.active)}
                          title={d.active ? 'Suspend' : 'Activate'}
                          style={{ ...iconBtn, color: d.active ? '#f57c00' : '#2e7d32' }}>
                          {d.active ? '⏸' : '▶'}
                        </button>
                        <button onClick={() => deleteDevice(d.device_id)}
                          title="Delete device"
                          style={{ ...iconBtn, color:'#e53935' }}>🗑</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </Section>

      <Section title="⚡ All Alerts" surface={surface} text={text}>
        {alerts.slice(0,10).length === 0
          ? <Empty>No alerts.</Empty>
          : alerts.slice(0,10).map(a => (
            <div key={a.id} style={aRow}>
              <span style={{ fontSize:18 }}>{a.alert_type==='fire' ? '🔥' : '🪚'}</span>
              <div style={{ flex:1, fontSize:13 }}>
                <strong>{a.device_id}</strong> · {a.zone}
                <span style={{ fontSize:11, color:'#aaa' }}>
                  {' '}· {new Date(a.created_at).toLocaleString()}
                </span>
              </div>
              <span style={{ ...badge,
                background: a.status==='resolved' ? '#e8f5e9' : '#ffebee',
                color:       a.status==='resolved' ? '#2e7d32' : '#c62828' }}>
                {a.status}
              </span>
            </div>
          ))}
      </Section>
    </div>
  )
}

function Section({ title, children, surface, text }) {
  return (
    <div style={{ background:surface, borderRadius:12, padding:'20px 22px',
      boxShadow:'0 1px 6px rgba(0,0,0,0.08)', color:text }}>
      <div style={{ fontSize:15, fontWeight:700, marginBottom:14 }}>{title}</div>
      {children}
    </div>
  )
}
function Empty({ children }) {
  return <div style={{ textAlign:'center', padding:'32px', color:'#aaa', fontSize:13 }}>{children}</div>
}

const statCard  = { borderRadius:10, padding:'16px 14px',
  display:'flex', flexDirection:'column', gap:4, boxShadow:'0 1px 6px rgba(0,0,0,0.07)' }
const errBanner = { background:'#ffebee', color:'#c62828', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const okBanner  = { background:'#e8f5e9', color:'#1b5e20', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const th     = { textAlign:'left', padding:'8px 12px', background:'#f9fafb',
  color:'#6b7280', fontWeight:600, borderBottom:'1px solid #e5e7eb', fontSize:12 }
const td     = { padding:'10px 12px', borderBottom:'1px solid #f3f4f6', verticalAlign:'middle' }
const badge  = { display:'inline-block', padding:'3px 9px', borderRadius:20, fontSize:11, fontWeight:600 }
const iconBtn= { background:'none', border:'none', cursor:'pointer', fontSize:17, padding:4, borderRadius:6 }
const aRow   = { display:'flex', alignItems:'center', gap:10, padding:'10px 12px',
  borderBottom:'1px solid #f3f4f6' }
""")

# ─────────────────────────────────────────────────────────────────────────────
# 8. APP.JSX (dark mode CSS variable injection + session persistence)
# ─────────────────────────────────────────────────────────────────────────────
write('frontend/src/App.jsx', r"""
import { useState } from 'react'
import Login          from './pages/Login.jsx'
import AdminDashboard from './pages/AdminDashboard.jsx'
import UserDashboard  from './pages/UserDashboard.jsx'
import BackendStatus  from './components/BackendStatus.jsx'

export default function App() {
  const [session, setSession] = useState(
    () => JSON.parse(sessionStorage.getItem('sf_session') || 'null')
  )

  function handleLogin(sess) {
    sessionStorage.setItem('sf_session', JSON.stringify(sess))
    setSession(sess)
  }

  function handleLogout() {
    sessionStorage.removeItem('sf_session')
    setSession(null)
  }

  if (!session) {
    return (
      <>
        <BackendStatus />
        <Login onLogin={handleLogin} />
      </>
    )
  }

  if (session.role === 'admin') {
    return <AdminDashboard session={session} onLogout={handleLogout} />
  }

  return <UserDashboard session={session} onLogout={handleLogout} />
}
""")

# ─────────────────────────────────────────────────────────────────────────────
# 9. BACKEND — AUTH ROUTES (add /register + /change-password)
# ─────────────────────────────────────────────────────────────────────────────
write('backend/src/routes/auth.js', r"""
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
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) return res.status(401).json({ error: error.message });

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
  } catch (err) {
    res.status(500).json({ error: err.message });
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
    if (error) return res.status(400).json({ error: error.message });

    await userModel.create({ name, email, role: 'customer' });
    res.status(201).json({ message: 'Account created. Please sign in.' });
  } catch (err) {
    res.status(500).json({ error: err.message });
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
    // Verify current token belongs to a valid session
    const { data: userData, error: ue } = await supabase.auth.getUser(token);
    if (ue) return res.status(401).json({ error: 'Invalid session' });

    // Re-authenticate with current password to verify it
    const { error: loginErr } = await supabase.auth.signInWithPassword({
      email: userData.user.email, password: currentPassword,
    });
    if (loginErr) return res.status(401).json({ error: 'Current password is incorrect' });

    // Update password
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
""")

# ─────────────────────────────────────────────────────────────────────────────
# 10. BACKEND — DEVICES ROUTES
# ─────────────────────────────────────────────────────────────────────────────
write('backend/src/routes/devices.js', r"""
const express = require('express');
const router  = express.Router();
const pool    = require('../config/db');
const supabase = require('../config/supabase');

/* helper — get user from bearer token */
async function getUser(req) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return null;
  const { data, error } = await supabase.auth.getUser(token);
  if (error || !data.user) return null;
  const r = await pool.query('SELECT * FROM users WHERE email=$1', [data.user.email]);
  return r.rows[0] || null;
}

// GET /api/devices — list devices owned by current user
router.get('/', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });
    const result = await pool.query(
      `SELECT d.*, u.email AS owner_email
       FROM devices d
       LEFT JOIN users u ON d.owner_id = u.id
       WHERE d.owner_id = $1
       ORDER BY d.created_at DESC`,
      [user.id]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/devices/all — admin: all devices
router.get('/all', async (req, res) => {
  try {
    const user = await getUser(req);
    if (!user || user.role !== 'admin')
      return res.status(403).json({ error: 'Admin only' });
    const result = await pool.query(
      `SELECT d.*, u.email AS owner_email
       FROM devices d
       LEFT JOIN users u ON d.owner_id = u.id
       ORDER BY d.created_at DESC`
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/devices — register a new device
router.post('/', async (req, res) => {
  const { device_id } = req.body;
  if (!device_id) return res.status(400).json({ error: 'device_id is required' });
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    // Check if device already claimed
    const existing = await pool.query(
      'SELECT * FROM devices WHERE device_id=$1', [device_id]
    );
    if (existing.rows.length > 0) {
      return res.status(409).json({ error: 'Device already registered' });
    }

    const result = await pool.query(
      `INSERT INTO devices (device_id, owner_id, active)
       VALUES ($1, $2, TRUE)
       RETURNING *`,
      [device_id, user.id]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PATCH /api/devices/:device_id/status — suspend or resume
router.patch('/:device_id/status', async (req, res) => {
  const { device_id } = req.params;
  const { active }    = req.body;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const filter = user.role === 'admin'
      ? 'WHERE device_id=$1'
      : 'WHERE device_id=$1 AND owner_id=$2';
    const params = user.role === 'admin'
      ? [device_id, active]
      : [device_id, user.id, active];

    // Build update
    const q = user.role === 'admin'
      ? 'UPDATE devices SET active=$2 WHERE device_id=$1 RETURNING *'
      : 'UPDATE devices SET active=$3 WHERE device_id=$1 AND owner_id=$2 RETURNING *';
    const p = user.role === 'admin'
      ? [device_id, active]
      : [device_id, user.id, active];

    const result = await pool.query(q, p);
    if (result.rows.length === 0)
      return res.status(404).json({ error: 'Device not found or not yours' });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/devices/:device_id — unregister device (removes all related data)
router.delete('/:device_id', async (req, res) => {
  const { device_id } = req.params;
  try {
    const user = await getUser(req);
    if (!user) return res.status(401).json({ error: 'Not authenticated' });

    const q = user.role === 'admin'
      ? 'DELETE FROM devices WHERE device_id=$1 RETURNING id'
      : 'DELETE FROM devices WHERE device_id=$1 AND owner_id=$2 RETURNING id';
    const p = user.role === 'admin' ? [device_id] : [device_id, user.id];

    const result = await pool.query(q, p);
    if (result.rows.length === 0)
      return res.status(404).json({ error: 'Device not found or not yours' });

    // Cascade: remove sensor readings & alerts for this device
    await pool.query('DELETE FROM sensor_readings WHERE device_id=$1', [device_id]);
    await pool.query('DELETE FROM alerts WHERE device_id=$1', [device_id]);

    res.json({ message: `Device ${device_id} deleted` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
""")

# ─────────────────────────────────────────────────────────────────────────────
# 11. BACKEND — ADMIN ROUTES
# ─────────────────────────────────────────────────────────────────────────────
write('backend/src/routes/admin.js', r"""
const express  = require('express');
const router   = express.Router();
const pool     = require('../config/db');
const supabase = require('../config/supabase');
const userModel = require('../models/userModel');

async function requireAdmin(req, res) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) { res.status(401).json({ error: 'Not authenticated' }); return null; }
  const { data, error } = await supabase.auth.getUser(token);
  if (error) { res.status(401).json({ error: 'Invalid token' }); return null; }
  const r = await pool.query('SELECT * FROM users WHERE email=$1', [data.user.email]);
  const user = r.rows[0];
  if (!user || user.role !== 'admin') {
    res.status(403).json({ error: 'Admin access required' });
    return null;
  }
  return user;
}

// GET /api/admin/users — all users
router.get('/users', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;
    const result = await pool.query('SELECT * FROM users ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/admin/users — create new admin user
router.post('/users', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;
    const { name, email, password, role } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'email and password are required' });
    }
    const { data, error } = await supabase.auth.admin.createUser({
      email, password,
      email_confirm: true,
      user_metadata: { name: name || email, role: role || 'admin' }
    });
    if (error) return res.status(400).json({ error: error.message });
    const profile = await userModel.create({ name: name || email, email, role: role || 'admin' });
    res.status(201).json(profile);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/admin/users/:id — delete user (never zero admins)
router.delete('/users/:id', async (req, res) => {
  try {
    const admin = await requireAdmin(req, res);
    if (!admin) return;

    const target = await userModel.getById(req.params.id);
    if (!target) return res.status(404).json({ error: 'User not found' });

    // Protect: never delete last admin
    if (target.role === 'admin') {
      const r = await pool.query("SELECT COUNT(*) FROM users WHERE role='admin'");
      if (parseInt(r.rows[0].count, 10) <= 1) {
        return res.status(400).json({ error: 'Cannot delete the last admin account' });
      }
    }

    await pool.query('DELETE FROM users WHERE id=$1', [req.params.id]);
    res.json({ message: 'User deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
""")

# ─────────────────────────────────────────────────────────────────────────────
# 12. BACKEND — userModel (add getAll, getById, delete)
# ─────────────────────────────────────────────────────────────────────────────
write('backend/src/models/userModel.js', r"""
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
""")

# ─────────────────────────────────────────────────────────────────────────────
# 13. BACKEND — index.js (mount new routes)
# ─────────────────────────────────────────────────────────────────────────────
write('backend/src/index.js', r"""
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
""")

# ─────────────────────────────────────────────────────────────────────────────
# 14. DB MIGRATION — devices table
# ─────────────────────────────────────────────────────────────────────────────
write('database/migrations/004_create_devices.sql', r"""
-- MIGRATION 004: devices table
-- Run FOURTH in Supabase SQL Editor (after users migration)

CREATE TABLE IF NOT EXISTS devices (
  id          SERIAL PRIMARY KEY,
  device_id   VARCHAR(50)   UNIQUE NOT NULL,
  owner_id    INTEGER       REFERENCES users(id) ON DELETE SET NULL,
  zone        VARCHAR(100),
  latitude    DOUBLE PRECISION,
  longitude   DOUBLE PRECISION,
  active      BOOLEAN       DEFAULT TRUE,
  last_seen   TIMESTAMPTZ,
  created_at  TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_owner
  ON devices(owner_id);
CREATE INDEX IF NOT EXISTS idx_devices_active
  ON devices(active);

-- Update last_seen when sensor data arrives for this device
-- (called from application layer via patch /devices/:id/status or MQTT handler)
""")

# ─────────────────────────────────────────────────────────────────────────────
# 15. DB SEED — admin user (must also be created in Supabase Auth)
# ─────────────────────────────────────────────────────────────────────────────
write('database/migrations/005_admin_seed.sql', r"""
-- MIGRATION 005: seed first admin user in the users table
-- NOTE: You must also create this user in Supabase Auth dashboard
--       (or via the Supabase CLI: supabase auth create-user)
--       Email: admin@smartforest.tz   Password: Admin@SmartForest2026

INSERT INTO users (name, email, role) VALUES
  ('System Admin', 'admin@smartforest.tz', 'admin')
ON CONFLICT (email) DO UPDATE SET role = 'admin';
""")

# ─────────────────────────────────────────────────────────────────────────────
# 16. SIMULATOR — rewritten with start/stop control + hardware ID labelling
# ─────────────────────────────────────────────────────────────────────────────
write('simulator/mqtt_simulator.py', r"""
#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates REAL hardware units. Each simulator device is labeled with a
# hardware-style ID:
#   Real hardware units  : smf-01a, smf-02a, smf-03a (SmartForest devices)
#   Simulator units      : smt-01a, smt-02a, smt-03a (simulator = "smt")

# Sensor types simulated:
#   MICROPHONE  - chainsaw / illegal logging detection  (alert threshold: 80 dB)
#   FLAME       - fire detection  (alert threshold: 55C or flame_detected=True)
#
# Usage:
#   pip install paho-mqtt --break-system-packages
#   python mqtt_simulator.py               # start (default 5-second interval)
#   python mqtt_simulator.py --stop        # graceful stop via sentinel file
#   SEND_INTERVAL=2 SPIKE_CHANCE=0.30 python mqtt_simulator.py
#
# Control signals:
#   Create a file named STOP_SIMULATOR in the same directory to stop the loop.
#   The script removes the file and exits cleanly.
#
# Env vars:
#   MQTT_BROKER_HOST    default: localhost
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   CLOUD_BACKEND_URL   Render / cloud backend URL
#   BACKEND_URL         manual override backend URL
#   SEND_INTERVAL       default: 5 (seconds between readings)
#   SPIKE_CHANCE        default: 0.20  (probability of alert-level reading)
#   USE_REAL_IDS        default: false  (set to "true" to use smf-* IDs)

import paho.mqtt.client as mqtt
import json, random, time, os, sys, argparse, signal
from datetime import datetime, timezone
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
BROKER       = os.getenv('MQTT_BROKER_HOST',   'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC',          'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL',  5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE',   0.20))
CLOUD_URL    = os.getenv('CLOUD_BACKEND_URL',   '').rstrip('/')
LOCAL_URL    = 'http://localhost:5000'

# Hardware ID prefix
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
MIC_PREFIX   = 'smf' if USE_REAL_IDS else 'smt'
FLM_PREFIX   = 'smf' if USE_REAL_IDS else 'smt'

SENTINEL = Path(__file__).parent / 'STOP_SIMULATOR'

# ── Sensor definitions ───────────────────────────────────────────────────────
ZONES = [
    {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95},
    {'zone': 'Kibiti-South', 'lat': -7.85, 'lng': 38.88},
    {'zone': 'Kibiti-East',  'lat': -7.78, 'lng': 39.05},
    {'zone': 'Kibiti-West',  'lat': -7.80, 'lng': 38.82},
]

# Hardware unit IDs
MIC_SENSORS   = [f'{MIC_PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_SENSORS = [f'{FLM_PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

import urllib.request, urllib.error

# ── Backend health check ──────────────────────────────────────────────────────
def check_backend(url, timeout=4):
    try:
        req = urllib.request.urlopen(url + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception:
        return False

def resolve_backend():
    manual = os.getenv('BACKEND_URL', '').rstrip('/')
    if manual and check_backend(manual):
        print(f'[SIM] Backend: manual override -> {manual}')
        return manual
    if CLOUD_URL and check_backend(CLOUD_URL):
        print(f'[SIM] Backend: cloud -> {CLOUD_URL}')
        return CLOUD_URL
    if check_backend(LOCAL_URL, timeout=2):
        print(f'[SIM] Backend: local -> {LOCAL_URL}')
        return LOCAL_URL
    print('[SIM] No backend reachable — MQTT only mode')
    return None

# ── Payload generators ────────────────────────────────────────────────────────
def make_microphone_payload(spike):
    zone = random.choice(ZONES)
    device = random.choice(MIC_SENSORS)
    return {
        'device_id'   : device,
        'sensor_type' : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : zone['zone'],
        'latitude'    : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'   : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'    : round(
            random.uniform(82, 98) if spike else random.uniform(20, 60), 2
        ),
    }

def make_flame_payload(spike):
    zone = random.choice(ZONES)
    device = random.choice(FLAME_SENSORS)
    return {
        'device_id'      : device,
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : zone['zone'],
        'latitude'       : round(zone['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(zone['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : spike,
        'temperature_c'  : round(
            random.uniform(58, 95) if spike else random.uniform(22, 40), 2
        ),
    }

# ── HTTP fallback ─────────────────────────────────────────────────────────────
def post_to_backend(backend_url, payload):
    if not backend_url:
        return
    try:
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            backend_url + '/api/sensors',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')

# ── MQTT callbacks ────────────────────────────────────────────────────────────
_running = True

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'[MQTT] Connected to broker at {BROKER}:{PORT}')
    else:
        print(f'[MQTT] Connection failed: reason code {reason_code}')
        sys.exit(1)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f'[MQTT] Disconnected ({reason_code}) — retrying...')

def graceful_stop(sig, frame):
    global _running
    print('\n[SIM] Signal received — stopping...')
    _running = False

# ── Argument parsing ──────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Hardware Simulator')
    p.add_argument('--stop', action='store_true',
                   help='Create STOP_SIMULATOR sentinel to stop a running instance')
    p.add_argument('--interval', type=float, default=INTERVAL,
                   help=f'Seconds between readings (default {INTERVAL})')
    p.add_argument('--spike',    type=float, default=SPIKE_CHANCE,
                   help=f'Alert spike probability 0–1 (default {SPIKE_CHANCE})')
    p.add_argument('--real-hw',  action='store_true',
                   help='Use smf-* IDs (real hardware IDs) instead of smt-* (simulator)')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _running, USE_REAL_IDS, MIC_SENSORS, FLAME_SENSORS, INTERVAL, SPIKE_CHANCE

    args = parse_args()

    if args.stop:
        SENTINEL.touch()
        print(f'[SIM] Created stop signal: {SENTINEL}')
        print('[SIM] The running simulator will stop at next cycle.')
        return

    INTERVAL     = args.interval
    SPIKE_CHANCE = args.spike
    if args.real_hw:
        USE_REAL_IDS = True
        MIC_SENSORS   = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_SENSORS = [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    hw_label = 'REAL HARDWARE' if USE_REAL_IDS else 'SIMULATOR (labeled as real HW)'
    print('[SIM] SmartForest IoT Hardware Simulator')
    print(f'[SIM] Hardware type : {hw_label}')
    print(f'[SIM] MIC  units    : {MIC_SENSORS}')
    print(f'[SIM] FLAME units   : {FLAME_SENSORS}')
    print(f'[SIM] Interval      : {INTERVAL}s | Spike chance: {int(SPIKE_CHANCE*100)}%')
    print()

    # Remove stale sentinel
    if SENTINEL.exists():
        SENTINEL.unlink()

    backend_url = resolve_backend()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect

    print(f'[MQTT] Connecting to {BROKER}:{PORT} ...')
    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f'[MQTT] ERROR: Cannot connect -> {e}')
        print('       Start Mosquitto: mosquitto -c mosquitto.conf')
        sys.exit(1)

    client.loop_start()
    time.sleep(1)

    print(f'[SIM] Topic : {TOPIC}')
    print(f'[SIM] Press Ctrl+C or run: python mqtt_simulator.py --stop')
    print('-' * 70)

    readings = 0
    alerts   = 0

    while _running:
        # Check sentinel file
        if SENTINEL.exists():
            print(f'[SIM] Stop sentinel detected. Exiting...')
            SENTINEL.unlink()
            break

        spike   = random.random() < SPIKE_CHANCE
        is_mic  = readings % 2 == 0

        if is_mic:
            payload = make_microphone_payload(spike)
            label   = (
                f"LOGGING-ALERT  {payload['device_id']}  sound:{payload['sound_db']}dB"
                if spike else
                f"mic-normal     {payload['device_id']}  sound:{payload['sound_db']}dB"
            )
        else:
            payload = make_flame_payload(spike)
            label   = (
                f"FIRE-ALERT     {payload['device_id']}  temp:{payload['temperature_c']}C"
                if spike else
                f"flame-normal   {payload['device_id']}  temp:{payload['temperature_c']}C"
            )

        client.publish(TOPIC, json.dumps(payload))
        post_to_backend(backend_url, payload)

        readings += 1
        if spike:
            alerts += 1

        ts = datetime.now().strftime('%H:%M:%S')
        print(f"{ts} | {label:<55} | {payload['zone']:<14} | r:{readings} a:{alerts}")

        time.sleep(INTERVAL)

    print(f'\n[SIM] Stopped. Readings: {readings} | Alerts triggered: {alerts}')
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    main()
""")

# ─────────────────────────────────────────────────────────────────────────────
print()
print('=' * 65)
print('  SmartForest patch applied successfully!')
print('=' * 65)
print()
print('NEXT STEPS:')
print()
print('1. DATABASE — run these SQL files in Supabase SQL Editor (in order):')
print('     database/migrations/001_create_users.sql')
print('     database/migrations/002_create_sensor_readings.sql')
print('     database/migrations/003_create_alerts.sql')
print('     database/migrations/004_create_devices.sql')
print('     database/migrations/005_admin_seed.sql')
print('     database/seeds/dev_seed.sql')
print()
print('2. SUPABASE AUTH — create the admin account in Supabase dashboard:')
print('     Email   : admin@smartforest.tz')
print('     Password: Admin@SmartForest2026')
print('     Set user_metadata: { "role": "admin", "name": "System Admin" }')
print()
print('3. ASSETS — place images into the frontend/public/assets/ folder:')
print('     public/assets/logo.png            (circular SmartForest logo)')
print('     public/assets/forest/forest1.jpg  (carousel image 1)')
print('     public/assets/forest/forest2.jpg  (carousel image 2)')
print('     public/assets/forest/forest3.jpg  (carousel image 3)')
print('     public/assets/forest/forest4.jpg  (carousel image 4)')
print()
print('4. MAP — Already uses OpenStreetMap / Leaflet (FREE, no API key needed).')
print('   If you later want Google Maps, install: @react-google-maps/api')
print('   and get a key from https://console.cloud.google.com/')
print()
print('5. FRONTEND:')
print('     cd frontend')
print('     npm install')
print('     npm run dev')
print()
print('6. BACKEND:')
print('     cd backend')
print('     npm install')
print('     npm run dev')
print()
print('7. SIMULATOR:')
print('     cd simulator')
print('     pip install paho-mqtt --break-system-packages')
print('     python mqtt_simulator.py              # start')
print('     python mqtt_simulator.py --stop       # stop')
print('     python mqtt_simulator.py --real-hw    # use smf-* IDs')
print('     USE_REAL_IDS=true python mqtt_simulator.py')
print()
print('8. TESTS:')
print('     cd backend && npm test')
print('     cd simulator && pytest tests/')
print()
print('Done! ✅')
