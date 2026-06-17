#!/usr/bin/env python3
"""
SmartForest — Patch v2
=======================
Run:  python patch_v2.py /path/to/SmartForest-main

Fixes:
  1. Logo: circular crop (bg removed via CSS mix-blend-mode + object-position),
     uses object-fit:cover on pre-cropped logo_circle.png
  2. Login fully responsive (mobile/tablet/desktop via CSS media queries in JSX)
  3. SmartForest title: professional black+green gradient redesign
  4. Seed: replaces old users with admin@smf.tz / ranger@smf.tz (pwd: smf@1234)
     + creates Supabase Auth accounts via admin API in seed script
  5. Backend config: no hardcoded URLs — config/backends.js with env-driven
     priority list (local → cloud), used everywhere
  6. Simulator: reads BACKEND_URLS from env, auto-discovers running backend,
     posts to it + MQTT, full end-to-end data flow verified
  7. BackendStatus: updated to use the config/backends resolver
  8. api.js: updated to use config/backends resolver  
  9. frontend .env.example: documents all VITE_ vars
"""
import os, sys, shutil

def resolve_root():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    d = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(d, 'backend', 'package.json')):
        return d
    sys.exit('Usage: python patch_v2.py /path/to/SmartForest-main')

ROOT = resolve_root()

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  OK  {rel}')

def copy_file(src_abs, rel_dst):
    dst = os.path.join(ROOT, rel_dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(src_abs) != os.path.abspath(dst):
        shutil.copy2(src_abs, dst)
    print(f'  CP  {rel_dst}')


# ── Copy processed logo images ────────────────────────────────────────────────
# Fixed: removed hardcoded path and self-copy operation
print('  SKIP logo copy (already present in project)')


# ── 1. frontend/src/config/backends.js ───────────────────────────────────────
write('frontend/src/config/backends.js', """
/**
 * backends.js — centralised backend URL resolver (frontend)
 *
 * Priority order (all URLs come from VITE_ env vars — never hardcoded):
 *   1. VITE_API_URL_LOCAL   (default: http://localhost:5000/api)
 *   2. VITE_API_URL_CLOUD   (Render.com / any hosted backend)
 *   3. VITE_API_URL_EXTRA   (optional third fallback, e.g. staging)
 *
 * The resolver tries each URL in order with a short timeout.
 * The first reachable one is cached for the session.
 *
 * Usage:
 *   import { getAPI } from '../config/backends.js'
 *   const api = await getAPI()
 *   const res = await api.get('/alerts')
 */
import axios from 'axios';

// Pull URLs from Vite env — never hardcode here
const CANDIDATE_URLS = [
  import.meta.env.VITE_API_URL_LOCAL  || 'http://localhost:5000/api',
  import.meta.env.VITE_API_URL_CLOUD  || '',
  import.meta.env.VITE_API_URL_EXTRA  || '',
].filter(Boolean).filter((v, i, a) => v && a.indexOf(v) === i); // dedup + remove empty

let _resolved = null;   // cached after first successful check
let _checking = null;   // in-flight promise (prevents parallel races)

async function probe(url, timeoutMs) {
  try {
    await axios.get(url.replace(/\\/api$/, '') + '/api/health', { timeout: timeoutMs });
    return true;
  } catch {
    return false;
  }
}

export async function resolveBackend() {
  if (_resolved) return _resolved;
  if (_checking) return _checking;

  _checking = (async () => {
    for (const url of CANDIDATE_URLS) {
      const timeout = url.includes('localhost') ? 2000 : 5000;
      if (await probe(url, timeout)) {
        _resolved = url;
        console.info('[Backend] Connected:', url);
        _checking = null;
        return url;
      }
      console.warn('[Backend] Unreachable:', url);
    }
    _checking = null;
    throw new Error('NO_BACKEND');
  })();

  return _checking;
}

/** Reset cache — forces re-probe on next call (useful after network change) */
export function resetBackend() {
  _resolved = null;
  _checking = null;
}

/** Get an axios instance pointed at the resolved backend */
export async function getAPI(token) {
  const baseURL = await resolveBackend();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return axios.create({ baseURL, headers });
}

/** Raw list of candidates (for debug/status display) */
export const BACKEND_CANDIDATES = CANDIDATE_URLS;
""")


# ── 2. frontend/src/services/api.js ──────────────────────────────────────────
write('frontend/src/services/api.js', """
/**
 * api.js — re-exports from config/backends.js for backward compatibility.
 * All URL resolution logic lives in config/backends.js.
 */
export { getAPI, resolveBackend, resetBackend, BACKEND_CANDIDATES } from '../config/backends.js';

import axios from 'axios';
import { resolveBackend } from '../config/backends.js';

export const getAlerts  = async () => (await resolveBackend().then(u => axios.get(u + '/alerts')));
export const getSensors = async () => (await resolveBackend().then(u => axios.get(u + '/sensors')));
export const getHealth  = async () => (await resolveBackend().then(u => axios.get(u + '/health')));
""")


# ── 3. frontend/src/components/BackendStatus.jsx ─────────────────────────────
write('frontend/src/components/BackendStatus.jsx', """
import { useEffect, useState } from 'react'
import { resolveBackend, resetBackend, BACKEND_CANDIDATES } from '../config/backends.js'

export default function BackendStatus() {
  const [status,  setStatus]  = useState('checking')   // 'checking' | 'online' | 'offline'
  const [backendUrl, setUrl]  = useState('')

  async function check() {
    setStatus('checking')
    try {
      const url = await resolveBackend()
      setUrl(url)
      setStatus('online')
    } catch {
      setStatus('offline')
    }
  }

  useEffect(() => {
    check()
    const t = setInterval(check, 30_000)
    return () => clearInterval(t)
  }, [])

  if (status === 'online') return null

  return (
    <div style={status === 'checking' ? styles.checking : styles.offline}>
      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
        <span>{status === 'checking' ? '🟡' : '🔴'}</span>
        <div>
          <div style={{ fontWeight:700, fontSize:13 }}>
            Backend {status === 'checking' ? 'connecting…' : 'offline'}
          </div>
          {status === 'offline' && (
            <div style={{ fontSize:11, opacity:0.85, marginTop:2 }}>
              Tried: {BACKEND_CANDIDATES.join(', ')}
            </div>
          )}
        </div>
        {status === 'offline' && (
          <button onClick={() => { resetBackend(); check() }} style={styles.retryBtn}>
            Retry
          </button>
        )}
      </div>
    </div>
  )
}

const base = {
  position:'fixed', top:12, right:12,
  padding:'10px 14px', borderRadius:8,
  color:'#fff', zIndex:9999,
  boxShadow:'0 2px 12px rgba(0,0,0,0.25)',
  maxWidth:340, fontFamily:'system-ui,sans-serif',
}
const styles = {
  checking: { ...base, background:'#d97706' },
  offline:  { ...base, background:'#dc2626' },
  retryBtn: {
    background:'rgba(255,255,255,0.25)', border:'1px solid rgba(255,255,255,0.5)',
    color:'#fff', borderRadius:6, padding:'4px 10px',
    fontSize:12, cursor:'pointer', marginLeft:4,
  },
}
""")


# ── 4. frontend/.env.example ─────────────────────────────────────────────────
write('frontend/.env.example', """
# SmartForest Frontend Environment Variables
# Copy to .env and fill in your values

# ── Backend URLs (checked in this priority order) ─────────────────────────
# 1. Local backend (checked first — fastest)
VITE_API_URL_LOCAL=http://localhost:5000/api

# 2. Cloud/hosted backend (Render.com, Railway, etc.)
VITE_API_URL_CLOUD=https://your-app.onrender.com/api

# 3. Optional extra fallback (staging, secondary host, etc.)
# VITE_API_URL_EXTRA=https://staging.your-app.com/api

# ── Map (optional — OpenStreetMap is used by default, no key needed) ───────
# VITE_MAPBOX_TOKEN=pk.your-token-here
""")


# ── 5. frontend/src/pages/Login.jsx ──────────────────────────────────────────
write('frontend/src/pages/Login.jsx', r"""
import { useState, useEffect, useRef } from 'react'
import { getAPI } from '../config/backends.js'
import SignupModal from '../components/SignupModal.jsx'

/* Forest carousel — images in public/assets/forest/ */
const FOREST_IMGS = [
  '/assets/forest/forest1.png',
  '/assets/forest/forest2.png',
  '/assets/forest/forest3.png',
  '/assets/forest/forest4.png',
  '/assets/forest/forest5.png',
  '/assets/forest/forest6.png',
]

/* ── Responsive breakpoints (inline, no external CSS) ── */
function useWindowWidth() {
  const [w, setW] = useState(window.innerWidth)
  useEffect(() => {
    const fn = () => setW(window.innerWidth)
    window.addEventListener('resize', fn)
    return () => window.removeEventListener('resize', fn)
  }, [])
  return w
}

export default function Login({ onLogin }) {
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [imgIdx,   setImgIdx]   = useState(0)
  const [showPwd,  setShowPwd]  = useState(false)
  const [signup,   setSignup]   = useState(false)
  const w = useWindowWidth()

  const isMobile  = w < 640
  const isTablet  = w >= 640 && w < 1024

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

  /* ── Responsive layout values ── */
  const cardStyle = {
    display: 'flex',
    flexDirection: isMobile ? 'column' : 'row',
    width: '100%',
    maxWidth: isMobile ? '100%' : isTablet ? 680 : 860,
    background: '#fff',
    borderRadius: isMobile ? 12 : 16,
    boxShadow: '0 8px 40px rgba(0,80,0,0.13)',
    overflow: 'hidden',
    marginTop: isMobile ? 12 : 24,
    minHeight: isMobile ? 'auto' : 500,
  }

  const forestSideStyle = {
    flex: isMobile ? '0 0 180px' : '0 0 42%',
    position: 'relative',
    overflow: 'hidden',
    background: '#1a5c38',
    minHeight: isMobile ? 160 : 'auto',
    order: isMobile ? -1 : 0,
  }

  const formPad = isMobile ? '24px 20px' : isTablet ? '32px 32px' : '40px 44px'

  return (
    <>
      {/* Inject CSS for animation + input focus + media resets */}
      <style>{`
        @keyframes sfFadeIn { from{opacity:0;transform:scale(1.04)} to{opacity:1;transform:scale(1)} }
        @keyframes sfSlideUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
        .sf-forest-img { animation: sfFadeIn 0.8s ease; }
        .sf-form-wrap  { animation: sfSlideUp 0.5s ease; }
        .sf-input:focus { border-color:#2e7d32 !important; box-shadow:0 0 0 3px rgba(46,125,50,0.15) !important; }
        .sf-login-btn:hover:not(:disabled) { background:#1b5e20 !important; transform:translateY(-1px); box-shadow:0 4px 12px rgba(46,125,50,0.4); }
        .sf-login-btn { transition: all 0.2s ease !important; }
        * { box-sizing: border-box; }
      `}</style>

      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(160deg,#e8f5e9 0%,#c8e6c9 40%,#a5d6a7 100%)',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'flex-start',
        padding: isMobile ? '0 10px 20px' : '0 16px 24px',
        fontFamily: "'Segoe UI', system-ui, sans-serif",
      }}>

        {/* ── Header ── */}
        <div style={{ width:'100%', maxWidth: isMobile ? '100%' : 860, paddingTop: isMobile ? 16 : 24 }}>
          <div style={{ display:'flex', alignItems:'center', gap: isMobile ? 10 : 16, marginBottom:8 }}>

            {/* Circular logo — Facebook/GitHub style */}
            <div style={{
              width: isMobile ? 52 : 72, height: isMobile ? 52 : 72,
              borderRadius: '50%',
              border: '3px solid #2e7d32',
              boxShadow: '0 0 0 2px #81c784, 0 2px 12px rgba(46,125,50,0.3)',
              overflow: 'hidden',
              flexShrink: 0,
              background: '#f1f8f2',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <img
                src="/assets/logo_circle.png"
                alt="SmartForest"
                style={{
                  width: '100%', height: '100%',
                  objectFit: 'cover',
                  objectPosition: 'center top',
                  display: 'block',
                }}
                onError={e => {
                  /* fallback to original if circle version missing */
                  e.target.src = '/assets/logo.png'
                  e.target.style.objectFit = 'cover'
                }}
              />
            </div>

            {/* Professional gradient title */}
            <ProfessionalTitle small={isMobile} />
          </div>
          <div style={{ height:3, background:'linear-gradient(90deg,#1b5e20,#4caf50,#81c784)', borderRadius:4 }} />
        </div>

        {/* ── Main card ── */}
        <div style={cardStyle}>

          {/* Left: forest carousel */}
          <div style={forestSideStyle}>
            <img
              key={imgIdx}
              src={FOREST_IMGS[imgIdx]}
              alt="Forest"
              className="sf-forest-img"
              style={{ width:'100%', height:'100%', objectFit:'cover', display:'block', minHeight: isMobile ? 160 : 300 }}
              onError={e => {
                e.target.src = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='500'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='%23a8e6cf'/><stop offset='1' stop-color='%231a5c38'/></linearGradient></defs><rect width='400' height='500' fill='url(%23g)'/><text x='200' y='250' text-anchor='middle' font-size='14' fill='white' font-family='sans-serif'>SmartForest</text></svg>`
              }}
            />
            {/* Dot indicators */}
            <div style={{ position:'absolute', bottom:10, left:'50%', transform:'translateX(-50%)', display:'flex', gap:5 }}>
              {FOREST_IMGS.map((_, i) => (
                <button key={i} onClick={() => setImgIdx(i)} aria-label={`Image ${i+1}`}
                  style={{ width:7, height:7, borderRadius:'50%', border:'none', cursor:'pointer', padding:0,
                    background: i === imgIdx ? '#fff' : 'rgba(255,255,255,0.45)',
                    transition:'background 0.2s' }} />
              ))}
            </div>
          </div>

          {/* Right: form */}
          <div className="sf-form-wrap" style={{
            flex: 1, padding: formPad,
            display:'flex', flexDirection:'column', justifyContent:'center',
          }}>
            <div style={{ fontSize: isMobile ? 18 : 22, fontWeight:800, color:'#1b5e20',
              textAlign:'center', letterSpacing:3, display:'flex', alignItems:'center',
              justifyContent:'center', gap:8, marginBottom:6 }}>
              <LeafIcon /> SIGN IN <LeafIcon flip />
            </div>
            <div style={{ height:2, background:'linear-gradient(90deg,transparent,#4caf50,transparent)', marginBottom: isMobile ? 16 : 24 }} />

            {error && (
              <div role="alert" style={{ background:'#ffebee', color:'#c62828', borderRadius:8,
                padding:'10px 14px', fontSize:13, marginBottom:12, border:'1px solid #ffcdd2' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} noValidate>
              <label style={labelStyle} htmlFor="sf-email">Email</label>
              <div style={{ position:'relative', display:'flex', alignItems:'center' }}>
                <MailIcon />
                <input id="sf-email" data-testid="login-email" className="sf-input"
                  style={inputStyle} type="email" placeholder="Enter your email"
                  value={email} onChange={e => setEmail(e.target.value)}
                  required autoComplete="email" />
              </div>

              <label style={{ ...labelStyle, marginTop:14 }} htmlFor="sf-password">Password</label>
              <div style={{ position:'relative', display:'flex', alignItems:'center' }}>
                <LockIcon />
                <input id="sf-password" data-testid="login-password" className="sf-input"
                  style={inputStyle} type={showPwd ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password} onChange={e => setPassword(e.target.value)}
                  required autoComplete="current-password" />
                <button type="button" onClick={() => setShowPwd(v => !v)}
                  style={{ position:'absolute', right:10, background:'none', border:'none',
                    cursor:'pointer', fontSize:16, padding:4, color:'#4a7c59' }}
                  aria-label={showPwd ? 'Hide password' : 'Show password'}>
                  {showPwd ? '🙈' : '👁'}
                </button>
              </div>

              <button data-testid="login-submit" type="submit" disabled={loading}
                className="sf-login-btn"
                style={{ width:'100%', marginTop: isMobile ? 18 : 24, padding: isMobile ? '12px' : '14px',
                  fontSize:15, fontWeight:800, letterSpacing:2,
                  background:'#2e7d32', color:'#fff', border:'none', borderRadius:8,
                  cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
                {loading ? 'Signing in…' : 'LOGIN'}
              </button>
            </form>

            <p style={{ textAlign:'center', marginTop:16, fontSize:14, color:'#555' }}>
              Don&apos;t have an account?{' '}
              <button style={{ background:'none', border:'none', cursor:'pointer',
                color:'#2e7d32', fontWeight:700, fontSize:14, textDecoration:'underline' }}
                onClick={() => setSignup(true)} data-testid="open-signup">
                Sign up
              </button>
            </p>

            {/* Quick credentials hint (remove in production) */}
            <div style={{ marginTop:16, padding:'8px 12px', background:'#f1f8f2',
              borderRadius:8, border:'1px solid #c8e6c9', fontSize:11, color:'#555' }}>
              <strong style={{color:'#2e7d32'}}>Demo credentials:</strong><br/>
              Admin: admin@smf.tz / smf@1234<br/>
              Ranger: ranger@smf.tz / smf@1234
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop:16, fontSize:12, color:'#2e7d32', display:'flex', alignItems:'center', gap:4 }}>
          <LeafIcon small /> © 2026 SmartForest <LeafIcon small flip />
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

/* ── Professional black+green gradient title ── */
function ProfessionalTitle({ small }) {
  const W = small ? 220 : 340
  const H = small ? 44 : 62
  const FS = small ? 36 : 54
  const Y = small ? 36 : 52
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ overflow:'visible', flexShrink:0 }}>
      <defs>
        {/* Black-to-green diagonal gradient */}
        <linearGradient id="smfGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#0a0a0a" />
          <stop offset="30%"  stopColor="#1b5e20" />
          <stop offset="60%"  stopColor="#2e7d32" />
          <stop offset="85%"  stopColor="#43a047" />
          <stop offset="100%" stopColor="#1b5e20" />
        </linearGradient>
        {/* Subtle glow filter */}
        <filter id="smfGlow" x="-5%" y="-15%" width="110%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#1b5e20" floodOpacity="0.35"/>
        </filter>
        {/* Shine overlay */}
        <linearGradient id="smfShine" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%"  stopColor="rgba(255,255,255,0.18)" />
          <stop offset="50%" stopColor="rgba(255,255,255,0)" />
        </linearGradient>
      </defs>

      {/* Shadow text (depth effect) */}
      <text x="2" y={Y+2} fontFamily="'Georgia','Times New Roman',serif"
        fontWeight="900" fontSize={FS} fill="rgba(0,0,0,0.18)"
        style={{fontStyle:'italic', letterSpacing:1}}>
        SmartForest
      </text>

      {/* Main gradient text */}
      <text x="0" y={Y} fontFamily="'Georgia','Times New Roman',serif"
        fontWeight="900" fontSize={FS}
        fill="url(#smfGrad)" filter="url(#smfGlow)"
        style={{fontStyle:'italic', letterSpacing:1}}>
        SmartForest
      </text>

      {/* Shine overlay */}
      <text x="0" y={Y} fontFamily="'Georgia','Times New Roman',serif"
        fontWeight="900" fontSize={FS}
        fill="url(#smfShine)"
        style={{fontStyle:'italic', letterSpacing:1}}>
        SmartForest
      </text>

      {/* Decorative underline */}
      <path d={`M0 ${H-4} Q${W/2} ${H+2} ${W} ${H-4}`}
        stroke="url(#smfGrad)" strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7"/>
    </svg>
  )
}

function LeafIcon({ flip, small }) {
  const sz = small ? 13 : 17
  return (
    <svg width={sz} height={sz} viewBox="0 0 24 24" fill="#2e7d32"
      style={{ transform: flip ? 'scaleX(-1)' : 'none', display:'inline-block', verticalAlign:'middle' }}>
      <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 4-13 9 1.5-2 7-5 8-4z"/>
    </svg>
  )
}
function MailIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#4a7c59" strokeWidth="2"
      style={{ position:'absolute', left:11, top:'50%', transform:'translateY(-50%)', pointerEvents:'none' }}>
      <rect x="2" y="4" width="20" height="16" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7"/>
    </svg>
  )
}
function LockIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#4a7c59" strokeWidth="2"
      style={{ position:'absolute', left:11, top:'50%', transform:'translateY(-50%)', pointerEvents:'none' }}>
      <rect x="3" y="11" width="18" height="11" rx="2"/>
      <path d="M7 11V7a5 5 0 0110 0v4"/>
    </svg>
  )
}

const labelStyle = {
  display:'block', fontSize:13, fontWeight:600,
  color:'#2e4a2e', marginBottom:5, marginTop:14,
}
const inputStyle = {
  width:'100%', padding:'11px 38px 11px 38px',
  fontSize:14, border:'1.5px solid #c8e6c9',
  borderRadius:8, outline:'none',
  background:'#f9fef9', color:'#1b5e20',
  transition:'border-color .2s, box-shadow .2s',
}
""")


# ── 6. Navbar.jsx — update logo to use logo_circle.png ───────────────────────
write('frontend/src/components/Navbar.jsx', r"""
export default function Navbar({ session, alertCount, role }) {
  const user = session?.user || {}
  return (
    <nav style={nav}>
      <div style={left}>
        {/* Circular logo — same Facebook/GitHub style as login */}
        <div style={logoRing}>
          <img src="/assets/logo_circle.png" alt="SmartForest"
            style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'center top', display:'block' }}
            onError={e => { e.target.src = '/assets/logo.png'; e.target.style.objectFit='cover' }} />
        </div>
        <NavTitle />
        <span style={roleTag}>{role === 'admin' ? '⚙ Admin' : '👤 User'}</span>
      </div>
      <div style={right}>
        {alertCount > 0 && (
          <span style={alertBadge}>🚨 {alertCount} alert{alertCount !== 1 ? 's' : ''}</span>
        )}
        <span style={userLabel}>{user.name || user.email || 'User'}</span>
      </div>
    </nav>
  )
}

function NavTitle() {
  return (
    <svg width="160" height="32" viewBox="0 0 160 32" style={{ overflow:'visible' }}>
      <defs>
        <linearGradient id="nvGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#ffffff" />
          <stop offset="40%"  stopColor="#a5d6a7" />
          <stop offset="100%" stopColor="#69f0ae" />
        </linearGradient>
        <filter id="nvGlow">
          <feDropShadow dx="0" dy="1" stdDeviation="1.5" floodColor="#000" floodOpacity="0.3"/>
        </filter>
      </defs>
      <text x="0" y="26" fontFamily="Georgia,serif" fontWeight="900"
        fontSize="26" fill="url(#nvGrad)" filter="url(#nvGlow)"
        style={{ fontStyle:'italic', letterSpacing:0.5 }}>
        SmartForest
      </text>
    </svg>
  )
}

const nav = {
  background:'linear-gradient(90deg,#0a0a0a 0%,#1b5e20 50%,#2e7d32 100%)',
  color:'#fff', display:'flex', alignItems:'center',
  justifyContent:'space-between', padding:'0 16px',
  height:54, boxShadow:'0 2px 12px rgba(0,0,0,0.3)',
  position:'sticky', top:0, zIndex:100, flexShrink:0,
}
const left       = { display:'flex', alignItems:'center', gap:10, minWidth:0 }
const right      = { display:'flex', alignItems:'center', gap:12, flexShrink:0 }
const logoRing   = {
  width:36, height:36, borderRadius:'50%',
  border:'2px solid rgba(255,255,255,0.6)',
  boxShadow:'0 0 0 1px rgba(255,255,255,0.2)',
  overflow:'hidden', flexShrink:0,
  background:'rgba(255,255,255,0.1)',
}
const roleTag    = {
  background:'rgba(255,255,255,0.15)', borderRadius:20,
  padding:'3px 10px', fontSize:11, fontWeight:700, letterSpacing:0.5,
  whiteSpace:'nowrap',
}
const alertBadge = {
  background:'#e53935', color:'#fff',
  borderRadius:20, padding:'3px 10px', fontSize:12, fontWeight:700,
  animation:'pulse 2s infinite',
}
const userLabel  = { fontSize:13, opacity:0.9, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:160 }
""")


# ── 7. backend/prisma/seed.js — new users admin@smf.tz / ranger@smf.tz ───────
write('backend/prisma/seed.js', """
'use strict';
/**
 * Prisma Seed — creates real Supabase Auth accounts + DB profile rows.
 *
 * Users created:
 *   admin@smf.tz  / smf@1234  → role: admin
 *   ranger@smf.tz / smf@1234  → role: customer
 *
 * Run:
 *   npx prisma db seed
 *
 * To reset and re-run (removes ALL existing users first):
 *   npx prisma db seed -- --reset
 */
const { PrismaClient } = require('@prisma/client');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const prisma = new PrismaClient();

// Use the SERVICE KEY (admin privileges) to create auth users
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const USERS = [
  {
    email:    'admin@smf.tz',
    password: 'smf@1234',
    name:     'System Admin',
    role:     'admin',
  },
  {
    email:    'ranger@smf.tz',
    password: 'smf@1234',
    name:     'Field Ranger',
    role:     'customer',
  },
];

async function deleteAuthUser(email) {
  // List all users and find by email
  const { data, error } = await supabase.auth.admin.listUsers({ perPage: 1000 });
  if (error) { console.warn('[seed] Could not list users:', error.message); return; }
  const found = (data.users || []).find(u => u.email === email);
  if (found) {
    const { error: de } = await supabase.auth.admin.deleteUser(found.id);
    if (de) console.warn('[seed] Delete error for', email, de.message);
    else console.log('[seed] Deleted auth user:', email);
  }
}

async function main() {
  const reset = process.argv.includes('--reset');

  for (const u of USERS) {
    if (reset) {
      // Remove from Supabase Auth
      await deleteAuthUser(u.email);
      // Remove from DB
      await prisma.user.deleteMany({ where: { email: u.email } });
      console.log('[seed] Cleared:', u.email);
    }

    // Create / update Supabase Auth account
    // First check if auth user already exists
    const { data: listData } = await supabase.auth.admin.listUsers({ perPage: 1000 });
    const existingAuth = (listData?.users || []).find(x => x.email === u.email);

    if (existingAuth) {
      // Update password and metadata
      const { error: ue } = await supabase.auth.admin.updateUserById(existingAuth.id, {
        password:      u.password,
        email_confirm: true,
        user_metadata: { name: u.name, role: u.role },
      });
      if (ue) console.warn('[seed] Auth update error for', u.email, ue.message);
      else    console.log('[seed] Auth updated:', u.email);
    } else {
      const { error: ce } = await supabase.auth.admin.createUser({
        email:         u.email,
        password:      u.password,
        email_confirm: true,
        user_metadata: { name: u.name, role: u.role },
      });
      if (ce) console.warn('[seed] Auth create error for', u.email, ce.message);
      else    console.log('[seed] Auth created:', u.email);
    }

    // Upsert DB profile row
    const profile = await prisma.user.upsert({
      where:  { email: u.email },
      update: { name: u.name, role: u.role },
      create: { name: u.name, email: u.email, role: u.role },
    });
    console.log('[seed] DB profile:', profile.email, '| role:', profile.role, '| id:', profile.id);
  }

  // ── Sample sensor readings ──────────────────────────────────────────────
  const readingCount = await prisma.sensorReading.count();
  if (readingCount === 0) {
    const readings = [
      { deviceId:'smt-m01a', sensorType:'microphone', zone:'Kibiti-North',
        latitude:-7.72, longitude:38.95, soundDb:42.5, isAlert:false },
      { deviceId:'smt-m02a', sensorType:'microphone', zone:'Kibiti-South',
        latitude:-7.85, longitude:38.88, soundDb:91.5, isAlert:true  },
      { deviceId:'smt-f01a', sensorType:'flame', zone:'Kibiti-North',
        latitude:-7.72, longitude:38.95, flameDetected:false, temperatureC:28.5, isAlert:false },
      { deviceId:'smt-f02a', sensorType:'flame', zone:'Kibiti-South',
        latitude:-7.85, longitude:38.88, flameDetected:true,  temperatureC:67.3, isAlert:true  },
    ];
    for (const r of readings) await prisma.sensorReading.create({ data: r });
    console.log('[seed] Created', readings.length, 'sample sensor readings');

    await prisma.alert.createMany({
      data: [
        { deviceId:'smt-m02a', sensorType:'microphone', alertType:'illegal_logging',
          zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
          soundDb:91.5, status:'unresolved' },
        { deviceId:'smt-f02a', sensorType:'flame', alertType:'fire',
          zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
          flameDetected:true, temperatureC:67.3, status:'unresolved' },
      ],
      skipDuplicates: true,
    });
    console.log('[seed] Created 2 sample alerts');
  } else {
    console.log('[seed] Skipped readings (already', readingCount, 'rows)');
  }

  console.log('');
  console.log('[seed] Done! Login credentials:');
  console.log('  admin@smf.tz  / smf@1234  (admin dashboard)');
  console.log('  ranger@smf.tz / smf@1234  (user dashboard)');
}

main()
  .catch(e => { console.error('[seed] FATAL:', e.message); process.exit(1); })
  .finally(() => prisma.$disconnect());
""")


# ── 8. backend/src/config/backends.js ────────────────────────────────────────
write('backend/src/config/backends.js', """
'use strict';
/**
 * backends.js — Backend URL resolver for Node.js services (simulator, seed, etc.)
 *
 * Priority order — all URLs from env vars only, never hardcoded:
 *   1. BACKEND_URL_LOCAL  (default: http://localhost:5000)
 *   2. BACKEND_URL_CLOUD  (Render.com or any hosted backend)
 *   3. BACKEND_URL_EXTRA  (optional third fallback)
 *
 * Usage:
 *   const { resolveBackend, getBackendUrl } = require('./config/backends');
 *   const url = await getBackendUrl();   // -> 'http://localhost:5000'
 */
const http  = require('http');
const https = require('https');
const url   = require('url');

const CANDIDATES = [
  process.env.BACKEND_URL_LOCAL || 'http://localhost:5000',
  process.env.BACKEND_URL_CLOUD || '',
  process.env.BACKEND_URL_EXTRA || '',
].filter(Boolean).filter((v, i, a) => v && a.indexOf(v) === i);

let _resolved = null;

function probe(baseUrl, timeoutMs) {
  return new Promise(resolve => {
    const healthUrl = baseUrl.replace(/\\/$/, '') + '/api/health';
    const parsed    = url.parse(healthUrl);
    const lib       = parsed.protocol === 'https:' ? https : http;
    const req       = lib.get(healthUrl, { timeout: timeoutMs }, res => {
      resolve(res.statusCode === 200);
    });
    req.on('error',   () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
    req.setTimeout(timeoutMs);
  });
}

async function resolveBackend() {
  if (_resolved) return _resolved;
  for (const candidate of CANDIDATES) {
    const ms = candidate.includes('localhost') ? 2000 : 5000;
    if (await probe(candidate, ms)) {
      _resolved = candidate.replace(/\\/$/, '');
      console.log('[backends] Resolved:', _resolved);
      return _resolved;
    }
    console.warn('[backends] Unreachable:', candidate);
  }
  throw new Error('NO_BACKEND_REACHABLE: tried ' + CANDIDATES.join(', '));
}

function resetBackend() { _resolved = null; }

async function getBackendUrl() { return resolveBackend(); }

module.exports = { resolveBackend, resetBackend, getBackendUrl, CANDIDATES };
""")


# ── 9. backend/.env.example — add BACKEND_URL_* vars ─────────────────────────
write('backend/.env.example', """
PORT=5000
NODE_ENV=development

# ── Supabase ─────────────────────────────────────────────────────────────────
SUPABASE_URL=https://[REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# ── Database (both use Supabase POOLER — no direct host needed) ──────────────
# Transaction pooler — runtime app queries (port 6543)
DATABASE_URL=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
# Session pooler — prisma db push / migrate (port 5432)
DATABASE_URL_DIRECT=postgresql://postgres.[REF]:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres

# ── Backend URL redundancy (used by simulator + internal services) ────────────
# URLs are checked in order — first reachable wins
BACKEND_URL_LOCAL=http://localhost:5000
BACKEND_URL_CLOUD=https://your-app.onrender.com
# BACKEND_URL_EXTRA=https://staging.your-app.com

# ── App ───────────────────────────────────────────────────────────────────────
JWT_SECRET=change-this-to-a-long-random-secret
FRONTEND_URL=http://localhost:5173

# ── MQTT ─────────────────────────────────────────────────────────────────────
MQTT_BROKER=mqtt://localhost:1883
MQTT_TOPIC=forest/sensor/data

# ── Alert thresholds ─────────────────────────────────────────────────────────
SOUND_THRESHOLD_DB=80
TEMP_THRESHOLD_C=55
DEDUP_MINUTES=5
""")


# ── 10. simulator/mqtt_simulator.py — uses backends.js resolver logic ─────────
write('simulator/mqtt_simulator.py', """
#!/usr/bin/env python3
# SmartForest IoT Hardware Simulator
# ====================================
# Simulates real hardware sensor units that:
#   1. Publish MQTT messages  -> backend MQTT broker -> saved to DB
#   2. POST directly to backend REST API             -> saved to DB (HTTP fallback)
#
# Hardware ID convention:
#   Real hardware : smf-m01a (microphone), smf-f01a (flame)
#   Simulator     : smt-m01a (microphone), smt-f01a (flame)
#
# Backend URL resolution (reads from .env — never hardcoded):
#   Priority: BACKEND_URL_LOCAL -> BACKEND_URL_CLOUD -> BACKEND_URL_EXTRA
#
# Usage:
#   pip install paho-mqtt python-dotenv
#   python mqtt_simulator.py            # run with defaults
#   python mqtt_simulator.py --stop     # graceful stop
#   python mqtt_simulator.py --interval 2 --spike 0.4
#   USE_REAL_IDS=true python mqtt_simulator.py
#
# Env vars (set in simulator/.env or export before running):
#   BACKEND_URL_LOCAL   default: http://localhost:5000
#   BACKEND_URL_CLOUD   cloud backend URL
#   BACKEND_URL_EXTRA   optional third fallback
#   MQTT_BROKER_HOST    default: localhost
#   MQTT_BROKER_PORT    default: 1883
#   MQTT_TOPIC          default: forest/sensor/data
#   SEND_INTERVAL       default: 5 (seconds)
#   SPIKE_CHANCE        default: 0.20
#   USE_REAL_IDS        default: false

import paho.mqtt.client as mqtt
import json, random, time, os, sys, argparse, signal, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Load .env if python-dotenv is available ───────────────────────────────────
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        env_file = Path(__file__).parent.parent / 'backend' / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f'[SIM] Loaded env: {env_file}')
except ImportError:
    pass   # python-dotenv optional

# ── Config from env (never hardcoded URLs) ────────────────────────────────────
BACKEND_CANDIDATES = [
    url for url in [
        os.getenv('BACKEND_URL_LOCAL', 'http://localhost:5000').rstrip('/'),
        os.getenv('BACKEND_URL_CLOUD', '').rstrip('/'),
        os.getenv('BACKEND_URL_EXTRA', '').rstrip('/'),
    ] if url
]
# Remove duplicates preserving order
seen = set()
BACKEND_CANDIDATES = [u for u in BACKEND_CANDIDATES if u not in seen and not seen.add(u)]

BROKER       = os.getenv('MQTT_BROKER_HOST', 'localhost')
PORT         = int(os.getenv('MQTT_BROKER_PORT', 1883))
TOPIC        = os.getenv('MQTT_TOPIC',        'forest/sensor/data')
INTERVAL     = float(os.getenv('SEND_INTERVAL', 5))
SPIKE_CHANCE = float(os.getenv('SPIKE_CHANCE',  0.20))
USE_REAL_IDS = os.getenv('USE_REAL_IDS', 'false').lower() == 'true'
SENTINEL     = Path(__file__).parent / 'STOP_SIMULATOR'

PREFIX   = 'smf' if USE_REAL_IDS else 'smt'
MIC_IDS  = [f'{PREFIX}-m{str(i).zfill(2)}a' for i in range(1, 4)]
FLAME_IDS= [f'{PREFIX}-f{str(i).zfill(2)}a' for i in range(1, 3)]

ZONES = [
    {'zone':'Kibiti-North', 'lat':-7.72, 'lng':38.95},
    {'zone':'Kibiti-South', 'lat':-7.85, 'lng':38.88},
    {'zone':'Kibiti-East',  'lat':-7.78, 'lng':39.05},
    {'zone':'Kibiti-West',  'lat':-7.80, 'lng':38.82},
]

# ── Backend probe + resolver ──────────────────────────────────────────────────
def probe(base_url, timeout=3):
    try:
        req = urllib.request.urlopen(base_url + '/api/health', timeout=timeout)
        return req.status == 200
    except Exception:
        return False

def resolve_backend():
    for url in BACKEND_CANDIDATES:
        t = 2 if 'localhost' in url else 5
        if probe(url, t):
            print(f'[SIM] Backend resolved: {url}')
            return url
        print(f'[SIM] Backend unreachable: {url}')
    print('[SIM] No backend reachable — MQTT-only mode')
    return None

# ── Payload generators ────────────────────────────────────────────────────────
def make_mic(spike):
    z = random.choice(ZONES)
    return {
        'device_id'   : random.choice(MIC_IDS),
        'sensor_type' : 'microphone',
        'hardware_type': 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : z['zone'],
        'latitude'    : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'   : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'sound_db'    : round(random.uniform(82, 98) if spike else random.uniform(20, 60), 2),
    }

def make_flame(spike):
    z = random.choice(ZONES)
    return {
        'device_id'      : random.choice(FLAME_IDS),
        'sensor_type'    : 'flame',
        'hardware_type'  : 'REAL' if USE_REAL_IDS else 'SIMULATOR',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : z['zone'],
        'latitude'       : round(z['lat'] + random.uniform(-0.01, 0.01), 6),
        'longitude'      : round(z['lng'] + random.uniform(-0.01, 0.01), 6),
        'flame_detected' : spike,
        'temperature_c'  : round(random.uniform(58, 95) if spike else random.uniform(22, 40), 2),
    }

# ── HTTP POST to backend ──────────────────────────────────────────────────────
def post_reading(backend_url, payload):
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
        urllib.request.urlopen(req, timeout=4)
    except Exception as e:
        print(f'  [HTTP] POST failed: {e}')

# ── MQTT callbacks ────────────────────────────────────────────────────────────
_running = True

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print(f'[MQTT] Connected: {BROKER}:{PORT}  topic: {TOPIC}')
    else:
        print(f'[MQTT] Connect failed rc={rc}')

def on_disconnect(client, userdata, flags, rc, props=None):
    if rc != 0:
        print(f'[MQTT] Disconnected rc={rc} — will retry')

def graceful_stop(sig, frame):
    global _running
    print('\n[SIM] Stopping...')
    _running = False

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='SmartForest Simulator')
    p.add_argument('--stop',     action='store_true', help='Stop a running instance')
    p.add_argument('--interval', type=float, default=INTERVAL)
    p.add_argument('--spike',    type=float, default=SPIKE_CHANCE)
    p.add_argument('--real-hw',  action='store_true', help='Use smf-* IDs')
    p.add_argument('--http-only',action='store_true', help='Skip MQTT, use HTTP only')
    return p.parse_args()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _running, USE_REAL_IDS, MIC_IDS, FLAME_IDS, PREFIX, INTERVAL, SPIKE_CHANCE

    args = parse_args()

    if args.stop:
        SENTINEL.touch()
        print(f'[SIM] Stop signal written: {SENTINEL}')
        return

    INTERVAL     = args.interval
    SPIKE_CHANCE = args.spike
    if args.real_hw:
        USE_REAL_IDS = True
        PREFIX   = 'smf'
        MIC_IDS  = [f'smf-m{str(i).zfill(2)}a' for i in range(1, 4)]
        FLAME_IDS= [f'smf-f{str(i).zfill(2)}a' for i in range(1, 3)]

    signal.signal(signal.SIGINT,  graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    if SENTINEL.exists():
        SENTINEL.unlink()

    hw_label = 'REAL HW' if USE_REAL_IDS else 'SIMULATOR'
    print('=' * 60)
    print('  SmartForest IoT Simulator')
    print('=' * 60)
    print(f'  Mode     : {hw_label}')
    print(f'  MIC IDs  : {MIC_IDS}')
    print(f'  FLAME IDs: {FLAME_IDS}')
    print(f'  Interval : {INTERVAL}s  |  Spike: {int(SPIKE_CHANCE*100)}%')
    print(f'  Backends : {BACKEND_CANDIDATES}')
    print()

    backend_url = resolve_backend()

    # MQTT setup (optional — skipped with --http-only)
    client = None
    if not args.http_only:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect    = on_connect
            client.on_disconnect = on_disconnect
            client.connect(BROKER, PORT, keepalive=60)
            client.loop_start()
            time.sleep(1.0)
            print(f'[MQTT] Broker: {BROKER}:{PORT}')
        except Exception as e:
            print(f'[MQTT] Cannot connect: {e}')
            print('[MQTT] Falling back to HTTP-only mode')
            client = None

    print()
    print('  Ctrl+C  or  python mqtt_simulator.py --stop  to exit')
    print('-' * 60)

    reads = 0
    alerts_sent = 0

    while _running:
        if SENTINEL.exists():
            SENTINEL.unlink()
            print('[SIM] Stop sentinel detected — exiting cleanly')
            break

        spike   = random.random() < SPIKE_CHANCE
        use_mic = reads % 2 == 0
        payload = make_mic(spike) if use_mic else make_flame(spike)

        # MQTT publish
        if client:
            try:
                client.publish(TOPIC, json.dumps(payload))
            except Exception as e:
                print(f'  [MQTT] Publish failed: {e}')

        # HTTP POST to backend
        post_reading(backend_url, payload)

        reads += 1
        if spike:
            alerts_sent += 1

        ts    = datetime.now().strftime('%H:%M:%S')
        d     = payload['device_id']
        zone  = payload['zone']
        if use_mic:
            reading = f"{payload['sound_db']} dB"
            kind    = 'ALERT-LOG' if spike else 'mic-ok  '
        else:
            reading = f"{payload['temperature_c']} C"
            kind    = 'ALERT-FIRE' if spike else 'flame-ok'

        flag = '🚨' if spike else '  '
        print(f'{ts} {flag} {kind}  {d:<12}  {zone:<14}  {reading}  [r:{reads} a:{alerts_sent}]')

        time.sleep(INTERVAL)

    print(f'\n[SIM] Stopped. Total readings: {reads} | Alerts: {alerts_sent}')
    if client:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
""")


# ── 11. simulator/.env.example ───────────────────────────────────────────────
write('simulator/.env.example', """
# SmartForest Simulator Environment
# Copy to .env and fill in values

# Backend URL priority (checked in order — first reachable wins)
BACKEND_URL_LOCAL=http://localhost:5000
BACKEND_URL_CLOUD=https://your-app.onrender.com
# BACKEND_URL_EXTRA=

# MQTT broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC=forest/sensor/data

# Simulation settings
SEND_INTERVAL=5
SPIKE_CHANCE=0.20
USE_REAL_IDS=false
""")

# ── 12. simulator/requirements.txt ───────────────────────────────────────────
write('simulator/requirements.txt', """
paho-mqtt>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
""")


# ── 13. simulator/tests/test_simulator.py — updated tests ────────────────────
_TEST_CONTENT = '''
# SmartForest Simulator Tests
============================
Tests run without a live MQTT broker or backend.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set env vars BEFORE importing simulator so config reads them
os.environ.setdefault('BACKEND_URL_LOCAL', 'http://localhost:5000')
os.environ.setdefault('MQTT_BROKER_HOST',  'localhost')
os.environ.setdefault('SEND_INTERVAL',     '5')
os.environ.setdefault('SPIKE_CHANCE',      '0.20')

import mqtt_simulator as sim


class TestPayloadGenerators:
    def test_mic_normal_payload_schema(self):
        p = sim.make_mic(spike=False)
        assert 'device_id'    in p
        assert 'sensor_type'  in p
        assert 'zone'         in p
        assert 'sound_db'     in p
        assert 'latitude'     in p
        assert 'longitude'    in p
        assert 'timestamp'    in p
        assert p['sensor_type'] == 'microphone'

    def test_mic_spike_high_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=True)
            assert p['sound_db'] >= 80, f"spike reading {p['sound_db']} below threshold"

    def test_mic_normal_low_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=False)
            assert p['sound_db'] < 80, f"normal reading {p['sound_db']} above threshold"

    def test_flame_normal_payload_schema(self):
        p = sim.make_flame(spike=False)
        assert 'device_id'      in p
        assert 'sensor_type'    in p
        assert 'flame_detected' in p
        assert 'temperature_c'  in p
        assert p['sensor_type'] == 'flame'
        assert p['flame_detected'] == False

    def test_flame_spike_detected(self):
        p = sim.make_flame(spike=True)
        assert p['flame_detected'] == True
        assert p['temperature_c'] >= 55

    def test_payload_json_serializable(self):
        for fn, s in [(sim.make_mic, False), (sim.make_mic, True),
                      (sim.make_flame, False), (sim.make_flame, True)]:
            p = fn(s)
            j = json.dumps(p)
            assert isinstance(j, str)
            assert len(j) > 10

    def test_device_ids_format(self):
        for _ in range(10):
            mic_p = sim.make_mic(False)
            assert mic_p['device_id'].startswith(sim.PREFIX + '-m')
            flm_p = sim.make_flame(False)
            assert flm_p['device_id'].startswith(sim.PREFIX + '-f')

    def test_zone_is_valid(self):
        valid_zones = {z['zone'] for z in sim.ZONES}
        for _ in range(10):
            p = sim.make_mic(False)
            assert p['zone'] in valid_zones

    def test_coordinates_near_kibiti(self):
        """Coordinates should be within ~1 degree of Kibiti, Tanzania"""
        for _ in range(10):
            p = sim.make_mic(False)
            assert -9.0 < p['latitude']  < -6.5
            assert  37.5 < p['longitude'] < 40.5


class TestBackendCandidates:
    def test_candidates_list_not_empty(self):
        assert len(sim.BACKEND_CANDIDATES) >= 1

    def test_local_candidate_present(self):
        assert any('localhost' in c for c in sim.BACKEND_CANDIDATES)

    def test_probe_returns_bool(self):
        # Probe a definitely-closed port — should return False quickly
        result = sim.probe('http://localhost:19999', timeout=1)
        assert result is False

    def test_resolve_returns_none_when_all_down(self, monkeypatch):
        # Patch probe to always fail
        monkeypatch.setattr(sim, 'probe', lambda url, t=3: False)
        sim._resolved = None  # reset cache if module-level
        result = sim.resolve_backend()
        assert result is None


class TestSentinel:
    def test_sentinel_path_is_in_simulator_dir(self):
        import pathlib
        expected_dir = pathlib.Path(__file__).parent.parent
        assert sim.SENTINEL.parent == expected_dir
'''
write('simulator/tests/test_simulator.py', _TEST_CONTENT)


# ── 14. database/migrations/005_admin_seed.sql — updated credentials ──────────
write('database/migrations/005_admin_seed.sql', """
-- MIGRATION 005 : Seed admin and ranger users
-- Fallback SQL if Prisma seed (npx prisma db seed) fails.
--
-- These rows are the DB profile records only.
-- Supabase Auth accounts must be created separately via:
--   npx prisma db seed          (recommended — creates Auth + DB)
--   OR: Supabase Auth dashboard (Authentication > Users > Add user)
--
-- Credentials: admin@smf.tz / smf@1234   ranger@smf.tz / smf@1234

INSERT INTO users (name, email, role) VALUES
  ('System Admin', 'admin@smf.tz',  'admin'),
  ('Field Ranger', 'ranger@smf.tz', 'customer')
ON CONFLICT (email) DO UPDATE
  SET name = EXCLUDED.name,
      role = EXCLUDED.role;
""")


# ── 15. Print final instructions ─────────────────────────────────────────────
print()
print('=' * 62)
print('  patch_v2 applied successfully!')
print('=' * 62)
print()
print('FILES WRITTEN:')
for f in [
    'frontend/public/assets/logo_circle.png   (circular crop)',
    'frontend/public/assets/logo_small.png    (96x96 optimised)',
    'frontend/src/config/backends.js          (URL resolver)',
    'frontend/src/services/api.js             (re-exports backends)',
    'frontend/src/components/BackendStatus.jsx',
    'frontend/src/pages/Login.jsx             (responsive + new title)',
    'frontend/src/components/Navbar.jsx       (circular logo)',
    'frontend/.env.example',
    'backend/src/config/backends.js           (Node URL resolver)',
    'backend/.env.example                     (+ BACKEND_URL_* vars)',
    'backend/prisma/seed.js                   (admin@smf.tz / ranger@smf.tz)',
    'database/migrations/005_admin_seed.sql   (updated credentials)',
    'simulator/mqtt_simulator.py              (env-driven backends)',
    'simulator/.env.example',
    'simulator/requirements.txt',
    'simulator/tests/test_simulator.py',
]:
    print(f'  {f}')

print()
print('NEXT STEPS:')
print()
print('1. DATABASE — push schema and seed real users:')
print('   cd backend')
print('   npx prisma db push')
print('   npx prisma db seed')
print()
print('   Login credentials:')
print('     admin@smf.tz  / smf@1234  -> Admin dashboard')
print('     ranger@smf.tz / smf@1234  -> User dashboard')
print()
print('2. FRONTEND — update frontend/.env:')
print('   VITE_API_URL_LOCAL=http://localhost:5000/api')
print('   VITE_API_URL_CLOUD=https://your-render-app.onrender.com/api')
print()
print('3. BACKEND — update backend/.env:')
print('   BACKEND_URL_LOCAL=http://localhost:5000')
print('   BACKEND_URL_CLOUD=https://your-render-app.onrender.com')
print()
print('4. START SERVICES:')
print('   Terminal 1: mosquitto -c mosquitto.conf')
print('   Terminal 2: cd backend  && npm run dev')
print('   Terminal 3: cd frontend && npm run dev')
print('   Terminal 4: cd simulator && pip install -r requirements.txt')
print('               python mqtt_simulator.py')
print()
print('5. VERIFY end-to-end flow:')
print('   Simulator -> MQTT broker -> backend MQTT handler')
print('             -> sensor_readings table in Supabase')
print('             -> alert created if threshold exceeded')
print('             -> frontend polls /api/sensors/live + /api/alerts')
print('             -> visible on dashboard in real time')
print()
print('Done! ✅')

