#!/usr/bin/env python3
"""
SmartForest Patch Script
========================
Fixes applied:
  1. Backend URL — single VITE_API_URL from .env, no hardcoded fallback.
     The .env.example is updated; Vercel users must set VITE_API_URL in
     Vercel → Project Settings → Environment Variables.
  2. Login page — header (logo + title) centred; font sizes bumped slightly;
     emoji password-toggle replaced with SVG icon.
  3. Admin Dashboard (from handwritten notes):
     - Navbar: remove "alerts" word, rename role tag to "System Admin" / "System".
     - Sidebar: add manage-users, manage-devices, system-performance, settings
       items with proper react-icons SVG replacements (no emoji).
     - Home content area: stat cards use react-icons (lucide) SVGs.
     - Admin/User/Log-report/System-breakdown cards described in notes added.
     - ALL emoji icons replaced with inline SVG icons (lucide-style).
  4. Replace all emoji with professional inline SVG icons everywhere.

Run from inside the SmartForest-main folder:
    python3 smartforest_patch.py

Or pass the path:
    python3 smartforest_patch.py /path/to/SmartForest-main
"""

import sys, os, shutil, textwrap
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
FRONTEND = ROOT / "frontend"
SRC      = FRONTEND / "src"

print(f"[SmartForest Patch] Root: {ROOT}")
assert FRONTEND.exists(), f"frontend/ not found under {ROOT}"


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────
def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [write] {path.relative_to(ROOT)}")

def backup(path: Path):
    bak = path.with_suffix(path.suffix + ".bak")
    if path.exists() and not bak.exists():
        shutil.copy2(path, bak)

def patch(path: Path, content: str):
    backup(path)
    write(path, content)


# ─────────────────────────────────────────────────────────────────────────────
# 1.  backend URL — single env-var, no hardcoded fallback
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] Fixing backend URL config …")

patch(FRONTEND / ".env.example", textwrap.dedent("""\
    # SmartForest Frontend — single backend URL
    # Set this to whichever backend you want the app to use.
    #
    # Local development:
    #   VITE_API_URL=http://localhost:5000/api
    #
    # Production (Render-hosted backend):
    #   VITE_API_URL=https://your-app.onrender.com/api
    #
    # ⚠ On Vercel you MUST set this in:
    #   Vercel → Project Settings → Environment Variables → VITE_API_URL
    #   Then trigger a redeploy so Vite bakes the value into the bundle.
    #
    VITE_API_URL=http://localhost:5000/api
"""))

# Update the actual .env only if VITE_API_URL is still pointing at localhost
# (don't overwrite a user's custom Render URL)
env_file = FRONTEND / ".env"
if env_file.exists():
    env_text = env_file.read_text()
else:
    env_text = ""

if "VITE_API_URL" not in env_text:
    with open(env_file, "a") as f:
        f.write("\nVITE_API_URL=http://localhost:5000/api\n")
    print("  [env] Added VITE_API_URL to .env")

# Fix backends.js — remove the hardcoded localhost fallback so Vercel build
# with no env var gives a clear error instead of silently using localhost.
patch(SRC / "config" / "backends.js", textwrap.dedent("""\
    /**
     * backends.js — single source of truth for the backend URL (frontend).
     *
     * ONE env var controls everything:
     *   VITE_API_URL   — set in frontend/.env  (local)
     *                    OR in Vercel → Project Settings → Environment Variables
     *
     * Vite bakes the value in at build time, so a redeploy is needed after
     * changing the variable on Vercel.
     *
     * Usage:
     *   import { getAPI } from '../config/backends.js'
     *   const api = await getAPI()
     *   const res = await api.get('/alerts')
     */
    import axios from 'axios';

    // MUST be set via env — no hardcoded fallback so misconfigurations are obvious.
    const API_URL = import.meta.env.VITE_API_URL;

    if (!API_URL) {
      console.error(
        '[SmartForest] VITE_API_URL is not set.\\n' +
        'Local: add VITE_API_URL=http://localhost:5000/api to frontend/.env\\n' +
        'Vercel: add VITE_API_URL in Project Settings → Environment Variables, then redeploy.'
      );
    }

    let _checked  = false;
    let _reachable = null;

    async function probe() {
      try {
        await axios.get(API_URL.replace(/\\/api$/, '') + '/api/health', { timeout: 6000 });
        return true;
      } catch {
        return false;
      }
    }

    /** Resolves to the configured API_URL. Throws NO_BACKEND if unreachable. */
    export async function resolveBackend() {
      if (!API_URL) throw new Error('NO_BACKEND');
      if (_checked && _reachable) return API_URL;
      const ok = await probe();
      _checked  = true;
      _reachable = ok;
      if (!ok) {
        console.warn('[Backend] Unreachable:', API_URL);
        throw new Error('NO_BACKEND');
      }
      console.info('[Backend] Connected:', API_URL);
      return API_URL;
    }

    /** Forces a fresh reachability check on next call. */
    export function resetBackend() {
      _checked  = false;
      _reachable = null;
    }

    /** Returns an axios instance pointed at the configured backend. */
    export async function getAPI(token) {
      const baseURL = await resolveBackend();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      return axios.create({ baseURL, headers });
    }

    /** The single configured URL (for status display / debugging). */
    export const BACKEND_URL = API_URL || '(VITE_API_URL not set)';
"""))

# api.js re-export — keep as-is (already correct)
patch(SRC / "services" / "api.js", textwrap.dedent("""\
    /**
     * api.js — re-exports from config/backends.js for backward compatibility.
     */
    export { getAPI, resolveBackend, resetBackend, BACKEND_URL } from '../config/backends.js';
"""))

# BackendStatus.jsx — replace emoji dots with SVG circles
patch(SRC / "components" / "BackendStatus.jsx", textwrap.dedent("""\
    import { useEffect, useState } from 'react'
    import { resolveBackend, resetBackend, BACKEND_URL } from '../config/backends.js'

    function DotIcon({ color }) {
      return (
        <svg width="12" height="12" viewBox="0 0 12 12" style={{ flexShrink:0 }}>
          <circle cx="6" cy="6" r="5" fill={color} />
        </svg>
      )
    }

    function RefreshIcon() {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
      )
    }

    export default function BackendStatus() {
      const [status, setStatus] = useState('checking')

      async function check() {
        setStatus('checking')
        try {
          await resolveBackend()
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
            <DotIcon color={status === 'checking' ? '#fbbf24' : '#fff'} />
            <div>
              <div style={{ fontWeight:700, fontSize:13 }}>
                Backend {status === 'checking' ? 'connecting…' : 'offline'}
              </div>
              {status === 'offline' && (
                <div style={{ fontSize:11, opacity:0.85, marginTop:2 }}>
                  {BACKEND_URL}
                </div>
              )}
            </div>
            {status === 'offline' && (
              <button onClick={() => { resetBackend(); check() }} style={styles.retryBtn}>
                <RefreshIcon /> Retry
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
        display:'flex', alignItems:'center', gap:4,
        background:'rgba(255,255,255,0.25)', border:'1px solid rgba(255,255,255,0.5)',
        color:'#fff', borderRadius:6, padding:'4px 10px',
        fontSize:12, cursor:'pointer', marginLeft:4,
      },
    }
"""))


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Login page — centre header, bump font sizes, remove emoji eye icon
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] Patching Login page …")

patch(SRC / "pages" / "Login.jsx", textwrap.dedent(r"""
    import { useState, useEffect } from 'react'
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

      const isMobile = w < 640
      const isTablet = w >= 640 && w < 1024

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
          const reason    = err?.response?.data?.reason
          const serverMsg = err?.response?.data?.error
          if (err?.message === 'NO_BACKEND') {
            setError('Cannot reach the backend server. Check your connection or try again shortly.')
          } else if (reason === 'invalid_credentials') {
            setError(serverMsg || 'Incorrect email or password.')
          } else if (reason === 'supabase_unreachable') {
            setError('Authentication service is temporarily unavailable. Please try again.')
          } else if (reason === 'profile_sync_failed') {
            setError('Signed in, but could not load your profile. Please try again.')
          } else if (serverMsg) {
            setError(serverMsg)
          } else {
            setError('Could not reach the server. Please check your connection and try again.')
          }
        } finally {
          setLoading(false)
        }
      }

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
        flex: isMobile ? '0 0 200px' : '0 0 44%',
        position: 'relative',
        overflow: 'hidden',
        background: '#1a5c38',
        minHeight: isMobile ? 180 : 'auto',
        order: isMobile ? -1 : 0,
      }

      const formPad = isMobile ? '28px 22px' : isTablet ? '36px 36px' : '44px 48px'

      return (
        <>
          <style>{`
            @keyframes sfFadeIn  { from{opacity:0;transform:scale(1.04)} to{opacity:1;transform:scale(1)} }
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

            {/* ── Header — centred on all screens ── */}
            <div style={{
              width:'100%',
              maxWidth: isMobile ? '100%' : 860,
              paddingTop: isMobile ? 20 : 28,
              display: 'flex', flexDirection: 'column', alignItems: 'center',
            }}>
              <div style={{ display:'flex', alignItems:'center', gap: isMobile ? 12 : 18, marginBottom:10 }}>

                {/* Circular logo */}
                <div style={{
                  width: isMobile ? 58 : 76, height: isMobile ? 58 : 76,
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
                    style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'center top', display:'block' }}
                    onError={e => { e.target.src = '/assets/logo.png'; e.target.style.objectFit = 'cover' }}
                  />
                </div>

                <ProfessionalTitle small={isMobile} />
              </div>

              {/* Divider line — full width of the content column */}
              <div style={{
                width:'100%',
                height:3,
                background:'linear-gradient(90deg,#1b5e20,#4caf50,#81c784)',
                borderRadius:4,
              }} />
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
                  style={{ width:'100%', height:'100%', objectFit:'cover', display:'block', minHeight: isMobile ? 180 : 320 }}
                  onError={e => {
                    e.target.src = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='500'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='%23a8e6cf'/><stop offset='1' stop-color='%231a5c38'/></linearGradient></defs><rect width='400' height='500' fill='url(%23g)'/><text x='200' y='250' text-anchor='middle' font-size='14' fill='white' font-family='sans-serif'>SmartForest</text></svg>`
                  }}
                />
                {/* Dot indicators */}
                <div style={{ position:'absolute', bottom:12, left:'50%', transform:'translateX(-50%)', display:'flex', gap:6 }}>
                  {FOREST_IMGS.map((_, i) => (
                    <button key={i} onClick={() => setImgIdx(i)} aria-label={`Image ${i+1}`}
                      style={{ width:8, height:8, borderRadius:'50%', border:'none', cursor:'pointer', padding:0,
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
                {/* Sign-in heading */}
                <div style={{ fontSize: isMobile ? 20 : 24, fontWeight:800, color:'#1b5e20',
                  textAlign:'center', letterSpacing:3, display:'flex', alignItems:'center',
                  justifyContent:'center', gap:8, marginBottom:6 }}>
                  <LeafIcon /> SIGN IN <LeafIcon flip />
                </div>
                <div style={{ height:2, background:'linear-gradient(90deg,transparent,#4caf50,transparent)', marginBottom: isMobile ? 18 : 26 }} />

                {error && (
                  <div role="alert" style={{ background:'#ffebee', color:'#c62828', borderRadius:8,
                    padding:'10px 14px', fontSize:14, marginBottom:14, border:'1px solid #ffcdd2' }}>
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

                  <label style={{ ...labelStyle, marginTop:16 }} htmlFor="sf-password">Password</label>
                  <div style={{ position:'relative', display:'flex', alignItems:'center' }}>
                    <LockIcon />
                    <input id="sf-password" data-testid="login-password" className="sf-input"
                      style={inputStyle} type={showPwd ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={password} onChange={e => setPassword(e.target.value)}
                      required autoComplete="current-password" />
                    <button type="button" onClick={() => setShowPwd(v => !v)}
                      style={{ position:'absolute', right:10, background:'none', border:'none',
                        cursor:'pointer', padding:4, color:'#4a7c59', display:'flex', alignItems:'center' }}
                      aria-label={showPwd ? 'Hide password' : 'Show password'}>
                      {showPwd ? <EyeOffIcon /> : <EyeIcon />}
                    </button>
                  </div>

                  <button data-testid="login-submit" type="submit" disabled={loading}
                    className="sf-login-btn"
                    style={{ width:'100%', marginTop: isMobile ? 20 : 26, padding: isMobile ? '13px' : '15px',
                      fontSize:16, fontWeight:800, letterSpacing:2,
                      background:'#2e7d32', color:'#fff', border:'none', borderRadius:8,
                      cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
                    {loading ? 'Signing in…' : 'LOGIN'}
                  </button>
                </form>

                <p style={{ textAlign:'center', marginTop:18, fontSize:15, color:'#555' }}>
                  Don&apos;t have an account?{' '}
                  <button style={{ background:'none', border:'none', cursor:'pointer',
                    color:'#2e7d32', fontWeight:700, fontSize:15, textDecoration:'underline' }}
                    onClick={() => setSignup(true)} data-testid="open-signup">
                    Sign up
                  </button>
                </p>

                {/* Demo credentials */}
                <div style={{ marginTop:16, padding:'10px 14px', background:'#f1f8f2',
                  borderRadius:8, border:'1px solid #c8e6c9', fontSize:12, color:'#555' }}>
                  <strong style={{color:'#2e7d32'}}>Demo credentials:</strong><br/>
                  Admin: admin@smf.tz / smf@1234<br/>
                  Ranger: ranger@smf.tz / smf@1234
                </div>
              </div>
            </div>

            {/* Footer */}
            <div style={{ marginTop:18, fontSize:13, color:'#2e7d32', display:'flex', alignItems:'center', gap:4 }}>
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

    /* ── Professional gradient title ── */
    function ProfessionalTitle({ small }) {
      const W  = small ? 230 : 350
      const H  = small ? 46  : 64
      const FS = small ? 38  : 56
      const Y  = small ? 38  : 54
      return (
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ overflow:'visible', flexShrink:0 }}>
          <defs>
            <linearGradient id="smfGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stopColor="#0a0a0a" />
              <stop offset="30%"  stopColor="#1b5e20" />
              <stop offset="60%"  stopColor="#2e7d32" />
              <stop offset="85%"  stopColor="#43a047" />
              <stop offset="100%" stopColor="#1b5e20" />
            </linearGradient>
            <filter id="smfGlow" x="-5%" y="-15%" width="110%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#1b5e20" floodOpacity="0.35"/>
            </filter>
            <linearGradient id="smfShine" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%"  stopColor="rgba(255,255,255,0.18)" />
              <stop offset="50%" stopColor="rgba(255,255,255,0)" />
            </linearGradient>
          </defs>
          <text x="2" y={Y+2} fontFamily="'Georgia','Times New Roman',serif"
            fontWeight="900" fontSize={FS} fill="rgba(0,0,0,0.18)"
            style={{fontStyle:'italic', letterSpacing:1}}>SmartForest</text>
          <text x="0" y={Y} fontFamily="'Georgia','Times New Roman',serif"
            fontWeight="900" fontSize={FS}
            fill="url(#smfGrad)" filter="url(#smfGlow)"
            style={{fontStyle:'italic', letterSpacing:1}}>SmartForest</text>
          <text x="0" y={Y} fontFamily="'Georgia','Times New Roman',serif"
            fontWeight="900" fontSize={FS}
            fill="url(#smfShine)"
            style={{fontStyle:'italic', letterSpacing:1}}>SmartForest</text>
          <path d={`M0 ${H-4} Q${W/2} ${H+2} ${W} ${H-4}`}
            stroke="url(#smfGrad)" strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7"/>
        </svg>
      )
    }

    /* ── Tiny inline SVG icons (lucide-style) ── */
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
          style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)', pointerEvents:'none' }}>
          <rect x="2" y="4" width="20" height="16" rx="2"/>
          <path d="m22 7-8.97 5.7a1.94 1.94 0 01-2.06 0L2 7"/>
        </svg>
      )
    }
    function LockIcon() {
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4a7c59" strokeWidth="2"
          style={{ position:'absolute', left:12, top:'50%', transform:'translateY(-50%)', pointerEvents:'none' }}>
          <rect x="3" y="11" width="18" height="11" rx="2"/>
          <path d="M7 11V7a5 5 0 0110 0v4"/>
        </svg>
      )
    }
    function EyeIcon() {
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      )
    }
    function EyeOffIcon() {
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
          <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>
      )
    }

    const labelStyle = {
      display:'block', fontSize:14, fontWeight:600,
      color:'#2e4a2e', marginBottom:6, marginTop:14,
    }
    const inputStyle = {
      width:'100%', padding:'12px 40px 12px 42px',
      fontSize:15, border:'1.5px solid #c8e6c9',
      borderRadius:8, outline:'none',
      background:'#f9fef9', color:'#1b5e20',
      transition:'border-color .2s, box-shadow .2s',
    }
"""))


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Navbar — remove emoji, rename role tag, remove "alerts" word from badge
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3] Patching Navbar …")

patch(SRC / "components" / "Navbar.jsx", textwrap.dedent("""\
    /* Navbar — professional SVG icons, no emoji */
    export default function Navbar({ session, alertCount, role }) {
      const user = session?.user || {}
      return (
        <nav style={nav}>
          <div style={left}>
            {/* Circular logo */}
            <div style={logoRing}>
              <img src="/assets/logo_circle.png" alt="SmartForest"
                style={{ width:'100%', height:'100%', objectFit:'cover', objectPosition:'center top', display:'block' }}
                onError={e => { e.target.src = '/assets/logo.png'; e.target.style.objectFit='cover' }} />
            </div>
            <NavTitle />
            <span style={roleTag}>
              {role === 'admin' ? <ShieldIcon /> : <UserIcon />}
              {' '}{role === 'admin' ? 'System Admin' : 'System'}
            </span>
          </div>
          <div style={right}>
            {alertCount > 0 && (
              <span style={alertBadge}>
                <BellIcon /> {alertCount}
              </span>
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

    /* Inline SVG icons */
    function ShieldIcon() {
      return (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
          style={{ display:'inline', verticalAlign:'middle', marginRight:3 }}>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      )
    }
    function UserIcon() {
      return (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
          style={{ display:'inline', verticalAlign:'middle', marginRight:3 }}>
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      )
    }
    function BellIcon() {
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
          style={{ display:'inline', verticalAlign:'middle', marginRight:4 }}>
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 01-3.46 0"/>
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
      display:'flex', alignItems:'center',
      background:'rgba(255,255,255,0.15)', borderRadius:20,
      padding:'3px 10px', fontSize:11, fontWeight:700, letterSpacing:0.5,
      whiteSpace:'nowrap',
    }
    const alertBadge = {
      display:'flex', alignItems:'center',
      background:'#e53935', color:'#fff',
      borderRadius:20, padding:'3px 10px', fontSize:12, fontWeight:700,
    }
    const userLabel  = { fontSize:13, opacity:0.9, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:160 }
"""))


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Sidebar — proper items from handwritten notes + SVG icons, no emoji
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] Patching Sidebar …")

patch(SRC / "components" / "Sidebar.jsx", textwrap.dedent("""\
    /* Sidebar — lucide-style SVG icons, no emoji.
       Items from handwritten notes:
         Home | Manage Devices | Manage Users | System Performance | Settings
       Bottom: Change Password | Mode toggle | Language | Logout
    */
    import { useState } from 'react'

    const LANGS = ['English','Swahili','French','Portuguese','Arabic']

    /* ── All inline SVG icons ─────────────────────────────────────────────── */
    const ICONS = {
      home:        ['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z', 'M9 22V12h6v10'],
      devices:     ['M8 6h13', 'M8 12h13', 'M8 18h13', 'M3 6h.01', 'M3 12h.01', 'M3 18h.01'],
      users:       ['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2', 'M9 7a4 4 0 100 8 4 4 0 000-8z',
                    'M23 21v-2a4 4 0 00-3-3.87', 'M16 3.13a4 4 0 010 7.75'],
      performance: ['M18 20V10', 'M12 20V4', 'M6 20v-6'],
      settings:    ['M12 20a8 8 0 100-16 8 8 0 000 16z',
                    'M12 14a2 2 0 100-4 2 2 0 000 4z'],
      password:    ['M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4'],
      sun:         ['M12 1v2','M12 21v2','M4.22 4.22l1.42 1.42','M18.36 18.36l1.42 1.42',
                    'M1 12h2','M21 12h2','M4.22 19.78l1.42-1.42','M18.36 5.64l1.42-1.42',
                    'M12 17a5 5 0 100-10 5 5 0 000 10z'],
      moon:        ['M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z'],
      globe:       ['M12 2a10 10 0 100 20A10 10 0 0012 2z',
                    'M2 12h20','M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20'],
      logout:      ['M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4',
                    'M16 17l5-5-5-5','M21 12H9'],
    }

    function SvgIcon({ name, size=20 }) {
      const d = ICONS[name] || ICONS.home
      if (name === 'devices') {
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {d.map((p, i) => <path key={i} d={p}/>)}
          </svg>
        )
      }
      if (Array.isArray(d)) {
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {d.map((p, i) => <path key={i} d={p}/>)}
          </svg>
        )
      }
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d={d}/>
        </svg>
      )
    }

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    export default function Sidebar({ active, onNav, onLogout, mode, onModeChange, lang, onLangChange }) {
      const [modeOpen, setModeOpen] = useState(false)
      const [langOpen, setLangOpen] = useState(false)

      const items = [
        { id:'home',        iconName:'home',        label:'Home'        },
        { id:'devices',     iconName:'devices',     label:'Devices'     },
        { id:'users',       iconName:'users',       label:'Users'       },
        { id:'performance', iconName:'performance', label:'Performance' },
        { id:'settings',    iconName:'settings',    label:'Settings'    },
      ]

      return (
        <aside style={{ ...sb, background: mode==='dark' ? '#1a2a1a' : '#1b5e20' }}>
          {items.map(it => (
            <SBBtn key={it.id} icon={<SvgIcon name={it.iconName} />} label={it.label}
              active={active===it.id} onClick={() => onNav(it.id)} />
          ))}

          {/* Divider */}
          <div style={{ width:40, height:1, background:'rgba(255,255,255,0.2)', margin:'6px 0' }} />

          {/* Change password */}
          <SBBtn icon={<SvgIcon name="password" />} label="Password" onClick={() => onNav('changepassword')} />

          {/* Mode toggle */}
          <div style={{ position:'relative' }}>
            <SBBtn icon={<SvgIcon name={mode==='dark' ? 'moon' : 'sun'} />} label="Mode"
              onClick={() => setModeOpen(v => !v)} />
            {modeOpen && (
              <div style={dropdown}>
                {['light','dark'].map(m => (
                  <button key={m} style={{ ...ddItem, fontWeight: mode===m ? 700 : 400 }}
                    onClick={() => { onModeChange(m); setModeOpen(false) }}>
                    {m === 'light' ? 'Light' : 'Dark'}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Language */}
          <div style={{ position:'relative' }}>
            <SBBtn icon={<SvgIcon name="globe" />} label="Language" onClick={() => setLangOpen(v => !v)} />
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

          {/* Logout — pushed to bottom */}
          <div style={{ marginTop:'auto' }}>
            <SBBtn icon={<SvgIcon name="logout" />} label="Logout" onClick={onLogout} danger />
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
            borderRadius:8,
            transition:'background .15s',
          }}
        >
          {icon}
          <span style={{ fontSize:9, fontWeight:600, letterSpacing:0.4, opacity:0.85 }}>
            {label}
          </span>
        </button>
      )
    }

    const sb = {
      width:68, minHeight:'calc(100vh - 54px)',
      display:'flex', flexDirection:'column',
      alignItems:'center', gap:2, paddingTop:12, paddingBottom:12,
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
"""))


# ─────────────────────────────────────────────────────────────────────────────
# 5.  AdminDashboard — replace emoji stat cards + section titles with SVG icons
#     Apply handwritten-notes spec:
#       - Remove "alerts" word from top bar  (done in Navbar)
#       - Remove "admin" word → "System Admin" (done in Navbar)
#       - Total Users counter = customers only (excludes admins) per notes
#       - Manage Devices icon/content area: first row = total/active/inactive cards
#         second row = live alerts for newly activated devices (within 1 hr)
#         last row = search/filter card showing all registered devices (5 rows)
#         each row: device id, active/down status, owner email; suspend & delete btns
#       - Home content: admin/user/log-report/system-breakdown cards
#       - System section: dashboard card for system resources (cpu, memory, db)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5] Patching AdminDashboard …")

patch(SRC / "pages" / "AdminDashboard.jsx", textwrap.dedent(r"""
    import { useState, useEffect, useRef, useCallback } from 'react'
    import Navbar  from '../components/Navbar.jsx'
    import Sidebar from '../components/Sidebar.jsx'
    import ChangePasswordModal from '../components/ChangePasswordModal.jsx'
    import { getAPI } from '../services/api.js'

    /* ── Inline SVG icon primitives (lucide-style, no emoji) ── */
    function Ico({ paths, size=16, color="currentColor", strokeWidth=2, fill="none" }) {
      return (
        <svg width={size} height={size} viewBox="0 0 24 24"
          fill={fill} stroke={color} strokeWidth={strokeWidth}
          strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink:0 }}>
          {[].concat(paths).map((p,i) => <path key={i} d={p}/>)}
        </svg>
      )
    }
    const I = {
      users:    ['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2','M9 7a4 4 0 100 8 4 4 0 000-8z','M23 21v-2a4 4 0 00-3-3.87','M16 3.13a4 4 0 010 7.75'],
      device:   ['M5 12.55a11 11 0 0114.08 0','M1.42 9a16 16 0 0121.16 0','M8.53 16.11a6 6 0 016.95 0','M12 20h.01'],
      active:   ['M22 11.08V12a10 10 0 11-5.93-9.14','M22 4L12 14.01l-3-3'],
      alert:    ['M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z','M12 9v4','M12 17h.01'],
      admin:    ['M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'],
      fire:     ['M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z'],
      saw:      ['M14.5 4h-5L7 7H4a2 2 0 00-2 2v9a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2h-3z','M10 13a2 2 0 104 0 2 2 0 00-4 0'],
      mic:      ['M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z','M19 10v2a7 7 0 01-14 0v-2','M12 19v4','M8 23h8'],
      temp:     ['M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z'],
      trash:    ['M3 6h18','M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2'],
      pause:    ['M6 4h4v16H6z','M14 4h4v16h-4z'],
      play:     ['M5 3l14 9-14 9V3z'],
      search:   ['M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0'],
      plus:     ['M12 5v14','M5 12h14'],
      check:    ['M20 6L9 17l-5-5'],
      report:   ['M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z','M14 2v6h6','M16 13H8','M16 17H8','M10 9H8'],
      cpu:      ['M9 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V5a2 2 0 00-2-2h-2','M9 3v2','M15 3v2','M9 21v-2','M15 21v-2','M3 9h2','M3 15h2','M19 9h2','M19 15h2'],
      db:       ['M12 2C6.48 2 2 4.02 2 6.5v11C2 19.98 6.48 22 12 22s10-2.02 10-4.5v-11C22 4.02 17.52 2 12 2z','M2 6.5c0 2.48 4.48 4.5 10 4.5s10-2.02 10-4.5','M2 12c0 2.48 4.48 4.5 10 4.5s10-2.02 10-4.5'],
    }

    /* ── dot status ── */
    function Dot({ on }) {
      return (
        <svg width="10" height="10" viewBox="0 0 10 10" style={{ flexShrink:0 }}>
          <circle cx="5" cy="5" r="4.5" fill={on ? '#22c55e' : '#9ca3af'} />
        </svg>
      )
    }

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
            api.get('/admin/users',  h),
            api.get('/devices/all',  h),
            api.get('/alerts',       h),
            api.get('/sensors/live', h),
            api.get('/alerts/count', h),
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
          r.style.setProperty('--bg',      '#121212')
          r.style.setProperty('--surface', '#1e1e1e')
          r.style.setProperty('--text',    '#e0e0e0')
        } else {
          r.style.setProperty('--bg',      '#f1f8f2')
          r.style.setProperty('--surface', '#ffffff')
          r.style.setProperty('--text',    '#1b2e1b')
        }
      }, [mode])

      function handleNav(id) {
        if (id === 'changepassword') { setShowPwdModal(true); return }
        setPage(id)
      }

      const bg      = mode === 'dark' ? '#121212' : '#f1f8f2'
      const surface = mode === 'dark' ? '#1e1e1e' : '#ffffff'
      const text    = mode === 'dark' ? '#e0e0e0' : '#1b2e1b'

      // Customers = non-admin users (per handwritten notes)
      const customers   = users.filter(u => u.role !== 'admin')
      const admins      = users.filter(u => u.role === 'admin')
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
                  users={users} customers={customers} devices={devices}
                  alerts={alerts} sensors={sensors} count={count}
                  admins={admins} activeCount={activeCount}
                  loading={loading} surface={surface} text={text}
                  session={session} onRefresh={load}
                />
              )}
              {page === 'devices' && (
                <AdminDevices devices={devices} alerts={alerts}
                  session={session} onRefresh={load} surface={surface} text={text} />
              )}
              {page === 'users' && (
                <AdminUserTable users={users} session={session} onRefresh={load}
                  surface={surface} text={text} />
              )}
              {page === 'performance' && (
                <SystemPerformance surface={surface} text={text} sensors={sensors}
                  devices={devices} loading={loading} />
              )}
              {page === 'settings' && (
                <SystemSettings surface={surface} text={text} />
              )}
            </main>
          </div>

          {showPwdModal && (
            <ChangePasswordModal session={session} onClose={() => setShowPwdModal(false)} />
          )}
        </div>
      )
    }

    /* ── Admin Home ─────────────────────────────────────────────────────── */
    function AdminHome({ customers, devices, alerts, sensors, count,
      admins, activeCount, loading, surface, text }) {

      return (
        <div style={{ display:'grid', gap:24 }}>
          {/* ── Stat row ── */}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))', gap:14 }}>
            {[
              { icon:<Ico paths={I.users} size={22} color="#1b5e20"/>,  label:'Total Customers', val:customers.length, color:'#1b5e20' },
              { icon:<Ico paths={I.device} size={22} color="#2563eb"/>, label:'Total Devices',   val:devices.length,   color:'#2563eb' },
              { icon:<Ico paths={I.active} size={22} color="#16a34a"/>, label:'Active Devices',  val:activeCount,      color:'#16a34a' },
              { icon:<Ico paths={I.alert} size={22} color="#dc2626"/>,  label:'Open Alerts',     val:count,            color:'#dc2626' },
              { icon:<Ico paths={I.admin} size={22} color="#7c3aed"/>,  label:'Admin Accounts',  val:admins.length,    color:'#7c3aed' },
            ].map(c => (
              <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
                {c.icon}
                <span style={{ fontSize:11, opacity:0.65, marginTop:4 }}>{c.label}</span>
                <span style={{ fontSize:28, fontWeight:800, color:c.color }}>
                  {loading ? '…' : c.val}
                </span>
              </div>
            ))}
          </div>

          {/* ── Log report card ── */}
          <Section title="Log Report" icon={<Ico paths={I.report} size={16} color="#6b7280"/>}
            surface={surface} text={text}>
            {alerts.slice(0, 8).length === 0
              ? <Empty>No alerts logged.</Empty>
              : alerts.slice(0, 8).map(a => (
                <div key={a.id} style={aRow}>
                  <span style={{ color: a.alert_type==='fire' ? '#dc2626' : '#92400e', marginRight:4 }}>
                    <Ico paths={a.alert_type==='fire' ? I.fire : I.saw} size={16} color="currentColor"/>
                  </span>
                  <div style={{ flex:1 }}>
                    <strong style={{ fontSize:13 }}>{a.device_id}</strong>
                    <span style={{ fontSize:11, color:'#6b7280' }}> · {a.zone} · {new Date(a.created_at).toLocaleString()}</span>
                  </div>
                  <span style={{ ...badge,
                    background: a.status==='resolved' ? '#dcfce7' : '#fee2e2',
                    color:       a.status==='resolved' ? '#16a34a' : '#dc2626' }}>
                    {a.status}
                  </span>
                </div>
              ))}
          </Section>

          {/* ── Live sensor readings ── */}
          <Section title="Live Sensor Readings" icon={<Ico paths={I.device} size={16} color="#6b7280"/>}
            surface={surface} text={text}>
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
                        <td style={td}>
                          <span style={{ display:'flex', alignItems:'center', gap:5 }}>
                            <Ico paths={s.sensor_type==='microphone' ? I.mic : I.fire} size={14}
                              color={s.sensor_type==='microphone' ? '#2563eb' : '#dc2626'}/>
                            {s.sensor_type === 'microphone' ? 'Mic' : 'Flame'}
                          </span>
                        </td>
                        <td style={td}>{s.zone}</td>
                        <td style={td}>
                          {s.sensor_type==='microphone' ? `${s.sound_db} dB` : `${s.temperature_c}°C`}
                        </td>
                        <td style={td}>
                          <span style={s.is_alert
                            ? { ...badge, background:'#fee2e2', color:'#dc2626' }
                            : { ...badge, background:'#dcfce7', color:'#16a34a' }}>
                            <Dot on={!s.is_alert} /> {s.is_alert ? 'Alert' : 'OK'}
                          </span>
                        </td>
                        <td style={{ ...td, fontSize:11, color:'#9ca3af' }}>
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

    /* ── User Management ────────────────────────────────────────────────── */
    function AdminUserTable({ users, session, onRefresh, surface, text }) {
      const [adding, setAdding] = useState(false)
      const [form,   setForm]   = useState({ name:'', email:'', password:'', role:'ranger' })
      const [error,  setError]  = useState('')
      const [ok,     setOk]     = useState('')
      const adminCount = users.filter(u => u.role === 'admin').length

      async function deleteUser(u) {
        if (u.role === 'admin' && adminCount <= 1) { alert('Cannot delete the last admin account.'); return }
        if (!confirm(`Delete user ${u.email}?`)) return
        try {
          const api = await getAPI()
          await api.delete(`/admin/users/${u.id}`,
            { headers: { Authorization: `Bearer ${session.token}` } })
          onRefresh()
        } catch (err) { alert(err?.response?.data?.error || 'Delete failed.') }
      }

      async function addAdmin(e) {
        e.preventDefault(); setError(''); setOk('')
        try {
          const api = await getAPI()
          await api.post('/admin/users',
            { ...form, role:'admin' },
            { headers: { Authorization: `Bearer ${session.token}` } })
          setOk(`Admin ${form.email} created.`)
          setForm({ name:'', email:'', password:'', role:'ranger' })
          setAdding(false); onRefresh()
        } catch (err) { setError(err?.response?.data?.error || 'Failed to create admin.') }
      }

      return (
        <Section title="User Management"
          icon={<Ico paths={I.users} size={16} color="#6b7280"/>}
          surface={surface} text={text}>
          <div style={{ display:'flex', justifyContent:'flex-end', marginBottom:12 }}>
            <button onClick={() => setAdding(v => !v)}
              style={{ display:'flex', alignItems:'center', gap:5,
                padding:'7px 16px', background:'#2e7d32', color:'#fff',
                border:'none', borderRadius:7, fontWeight:700, cursor:'pointer', fontSize:13 }}>
              <Ico paths={I.plus} size={14} color="#fff"/> {adding ? 'Cancel' : 'Add Admin'}
            </button>
          </div>

          {adding && (
            <div style={{ background:'#f9fef9', border:'1px solid #c8e6c9', borderRadius:8, padding:16, marginBottom:16 }}>
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
                    <span style={u.role==='admin'
                      ? { ...badge, background:'#dcfce7', color:'#15803d' }
                      : { ...badge, background:'#dbeafe', color:'#1d4ed8' }}>
                      {u.role}
                    </span>
                  </td>
                  <td style={{ ...td, fontSize:11, color:'#9ca3af' }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                  <td style={td}>
                    <button
                      title={u.role==='admin' && adminCount<=1 ? 'Cannot delete last admin' : 'Delete user'}
                      onClick={() => deleteUser(u)}
                      disabled={u.id === session?.user?.id}
                      style={{ ...iconBtn, color:'#dc2626', opacity: u.id===session?.user?.id ? 0.3 : 1 }}>
                      <Ico paths={I.trash} size={15} color="currentColor"/>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )
    }

    /* ── Admin Devices page — per handwritten spec ───────────────────────── */
    function AdminDevices({ devices, alerts, session, onRefresh, surface, text }) {
      const [search, setSearch]   = useState('')
      const [page,   setPage]     = useState(0)
      const PAGE_SIZE = 5

      // Set once after mount via useEffect — Date.now() never called during render
      const [mountedAt, setMountedAt] = useState(0)
      useEffect(() => { setMountedAt(Date.now()) }, [])

      const ONE_HOUR = 60 * 60 * 1000
      const recentlyActivated = mountedAt === 0 ? [] : devices.filter(d => {
        if (!d.activated_at) return false
        return (mountedAt - new Date(d.activated_at).getTime()) < ONE_HOUR
      })

      const filtered = devices.filter(d =>
        d.device_id?.toLowerCase().includes(search.toLowerCase()) ||
        d.owner_email?.toLowerCase().includes(search.toLowerCase())
      )
      const totalPages  = Math.ceil(filtered.length / PAGE_SIZE)
      const pageDevices = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

      const activeCount   = devices.filter(d => d.active).length
      const inactiveCount = devices.length - activeCount

      async function deleteDevice(id) {
        if (!confirm(`Delete device ${id}? All data will be removed.`)) return
        try {
          const api = await getAPI()
          await api.delete(`/devices/${id}`,
            { headers: { Authorization: `Bearer ${session.token}` } })
          onRefresh()
        } catch (err) { alert(err?.response?.data?.error || 'Delete failed.') }
      }

      async function toggleDevice(id, active) {
        try {
          const api = await getAPI()
          await api.patch(`/devices/${id}/status`, { active: !active },
            { headers: { Authorization: `Bearer ${session.token}` } })
          onRefresh()
        } catch (err) { alert(err?.response?.data?.error || 'Update failed.') }
      }

      return (
        <div style={{ display:'grid', gap:20 }}>
          {/* Row 1 — summary cards */}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:14 }}>
            {[
              { label:'Registered Devices', val:devices.length,   icon:<Ico paths={I.device} size={22} color="#2563eb"/>, color:'#2563eb' },
              { label:'Active Devices',     val:activeCount,       icon:<Ico paths={I.active} size={22} color="#16a34a"/>, color:'#16a34a' },
              { label:'Inactive Devices',   val:inactiveCount,     icon:<Ico paths={I.alert}  size={22} color="#9ca3af"/>, color:'#9ca3af' },
            ].map(c => (
              <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
                {c.icon}
                <span style={{ fontSize:11, opacity:0.65, marginTop:4 }}>{c.label}</span>
                <span style={{ fontSize:26, fontWeight:800, color:c.color }}>{c.val}</span>
              </div>
            ))}
          </div>

          {/* Row 2 — live alerts for newly activated devices (within 1 hr) */}
          <Section title="Live Alerts — Recently Activated Devices (last 1 hr)"
            icon={<Ico paths={I.alert} size={15} color="#dc2626"/>}
            surface={surface} text={text}>
            {recentlyActivated.length === 0
              ? <Empty>No newly activated devices in the last hour.</Empty>
              : recentlyActivated.map(d => (
                <div key={d.id} style={aRow}>
                  <Dot on={d.active} />
                  <strong style={{ fontSize:13, minWidth:120 }}>{d.device_id}</strong>
                  <span style={{ fontSize:12, color:'#6b7280', flex:1 }}>{d.owner_email || '—'}</span>
                  <span style={{ fontSize:11, color:'#6b7280' }}>{d.zone}</span>
                  <span style={{ ...badge,
                    background: d.active ? '#dcfce7' : '#fee2e2',
                    color:       d.active ? '#16a34a' : '#dc2626' }}>
                    {d.active ? 'Active' : 'Down'}
                  </span>
                </div>
              ))}
          </Section>

          {/* Row 3 — search/filter + paginated device table */}
          <Section title="All Registered Devices"
            icon={<Ico paths={I.search} size={15} color="#6b7280"/>}
            surface={surface} text={text}>
            {/* search bar */}
            <div style={{ display:'flex', gap:10, marginBottom:14 }}>
              <div style={{ position:'relative', flex:1 }}>
                <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)' }}>
                  <Ico paths={I.search} size={14} color="#9ca3af"/>
                </span>
                <input
                  type="text" placeholder="Filter by device ID or owner email…"
                  value={search} onChange={e => { setSearch(e.target.value); setPage(0) }}
                  style={{ width:'100%', padding:'8px 10px 8px 32px', fontSize:13,
                    border:'1.5px solid #e5e7eb', borderRadius:8, outline:'none' }}
                />
              </div>
            </div>

            {devices.length === 0
              ? <Empty>No devices in the system.</Empty>
              : (
                <>
                  <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
                    <thead><tr>
                      {['Device ID','Status','Owner Email','Location','Actions'].map(h =>
                        <th key={h} style={th}>{h}</th>)}
                    </tr></thead>
                    <tbody>
                      {pageDevices.map(d => (
                        <tr key={d.id}>
                          <td style={td}><strong>{d.device_id}</strong></td>
                          <td style={td}>
                            <span style={{ display:'flex', alignItems:'center', gap:5,
                              ...badge,
                              background: d.active ? '#dcfce7' : '#f3f4f6',
                              color:       d.active ? '#16a34a' : '#6b7280' }}>
                              <Dot on={d.active}/> {d.active ? 'Active' : 'Suspended'}
                            </span>
                          </td>
                          <td style={td}>{d.owner_email || '—'}</td>
                          <td style={td}>{d.zone || '—'}</td>
                          <td style={td}>
                            <div style={{ display:'flex', gap:8 }}>
                              <button onClick={() => toggleDevice(d.device_id, d.active)}
                                title={d.active ? 'Suspend' : 'Activate'}
                                style={{ ...iconBtn, color: d.active ? '#f59e0b' : '#16a34a' }}>
                                <Ico paths={d.active ? I.pause : I.play} size={15} color="currentColor"/>
                              </button>
                              <button onClick={() => deleteDevice(d.device_id)} title="Delete device"
                                style={{ ...iconBtn, color:'#dc2626' }}>
                                <Ico paths={I.trash} size={15} color="currentColor"/>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div style={{ display:'flex', justifyContent:'center', gap:8, marginTop:14 }}>
                      {Array.from({ length: totalPages }, (_, i) => (
                        <button key={i} onClick={() => setPage(i)}
                          style={{ padding:'4px 12px', borderRadius:6, border:'1.5px solid #e5e7eb',
                            background: i===page ? '#2e7d32' : '#fff',
                            color: i===page ? '#fff' : '#374151',
                            fontWeight:600, cursor:'pointer', fontSize:12 }}>
                          {i + 1}
                        </button>
                      ))}
                    </div>
                  )}
                </>
              )}
          </Section>

          {/* All Alerts */}
          <Section title="All Alerts"
            icon={<Ico paths={I.alert} size={15} color="#6b7280"/>}
            surface={surface} text={text}>
            {alerts.slice(0,10).length === 0
              ? <Empty>No alerts.</Empty>
              : alerts.slice(0,10).map(a => (
                <div key={a.id} style={aRow}>
                  <Ico paths={a.alert_type==='fire' ? I.fire : I.saw} size={16}
                    color={a.alert_type==='fire' ? '#dc2626' : '#92400e'}/>
                  <div style={{ flex:1, fontSize:13 }}>
                    <strong>{a.device_id}</strong> · {a.zone}
                    <span style={{ fontSize:11, color:'#9ca3af' }}> · {new Date(a.created_at).toLocaleString()}</span>
                  </div>
                  <span style={{ ...badge,
                    background: a.status==='resolved' ? '#dcfce7' : '#fee2e2',
                    color:       a.status==='resolved' ? '#16a34a' : '#dc2626' }}>
                    {a.status}
                  </span>
                </div>
              ))}
          </Section>
        </div>
      )
    }

    /* ── System Performance ─────────────────────────────────────────────── */
    function SystemPerformance({ surface, text, sensors, devices, loading }) {
      return (
        <div style={{ display:'grid', gap:20 }}>
          <Section title="System Resources"
            icon={<Ico paths={I.cpu} size={16} color="#6b7280"/>}
            surface={surface} text={text}>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(140px,1fr))', gap:14 }}>
              {[
                { label:'CPU',       icon:<Ico paths={I.cpu}  size={20} color="#7c3aed"/>, val:'—', unit:'%',  color:'#7c3aed' },
                { label:'Memory',    icon:<Ico paths={I.db}   size={20} color="#2563eb"/>, val:'—', unit:'%',  color:'#2563eb' },
                { label:'DB',        icon:<Ico paths={I.db}   size={20} color="#16a34a"/>, val:'—', unit:'ms', color:'#16a34a' },
                { label:'Uptime',    icon:<Ico paths={I.check} size={20} color="#f59e0b"/>,val:'—', unit:'hr', color:'#f59e0b' },
              ].map(c => (
                <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
                  {c.icon}
                  <span style={{ fontSize:11, opacity:0.65, marginTop:4 }}>{c.label}</span>
                  <span style={{ fontSize:22, fontWeight:800, color:c.color }}>{c.val}{c.unit}</span>
                </div>
              ))}
            </div>
            <p style={{ fontSize:12, color:'#9ca3af', marginTop:12 }}>
              System resource metrics require a backend /system/stats endpoint.
              Connect your backend to display live CPU, memory, DB latency and uptime.
            </p>
          </Section>

          <Section title="Sensor Summary"
            icon={<Ico paths={I.device} size={16} color="#6b7280"/>}
            surface={surface} text={text}>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:14 }}>
              {[
                { label:'Total Sensors',  val: loading ? '…' : sensors.length,                              color:'#2563eb' },
                { label:'Alerting',       val: loading ? '…' : sensors.filter(s=>s.is_alert).length,        color:'#dc2626' },
                { label:'Total Devices',  val: loading ? '…' : devices.length,                              color:'#1b5e20' },
              ].map(c => (
                <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
                  <span style={{ fontSize:11, opacity:0.65 }}>{c.label}</span>
                  <span style={{ fontSize:24, fontWeight:800, color:c.color }}>{c.val}</span>
                </div>
              ))}
            </div>
          </Section>
        </div>
      )
    }

    /* ── System Settings placeholder ─────────────────────────────────────── */
    function SystemSettings({ surface, text }) {
      return (
        <Section title="System Settings"
          icon={<Ico paths={['M12 20a8 8 0 100-16 8 8 0 000 16z','M12 14a2 2 0 100-4 2 2 0 000 4z']} size={16} color="#6b7280"/>}
          surface={surface} text={text}>
          <p style={{ color:'#9ca3af', fontSize:13, padding:'16px 0' }}>
            System configuration settings will appear here.
          </p>
        </Section>
      )
    }

    /* ── Section wrapper ─────────────────────────────────────────────────── */
    function Section({ title, icon, children, surface, text }) {
      return (
        <div style={{ background:surface, borderRadius:12, padding:'20px 22px',
          boxShadow:'0 1px 6px rgba(0,0,0,0.07)', color:text }}>
          <div style={{ display:'flex', alignItems:'center', gap:8,
            fontSize:15, fontWeight:700, marginBottom:16, color:text }}>
            {icon} {title}
          </div>
          {children}
        </div>
      )
    }
    function Empty({ children }) {
      return <div style={{ textAlign:'center', padding:'32px', color:'#9ca3af', fontSize:13 }}>{children}</div>
    }

    /* ── Shared style tokens ─────────────────────────────────────────────── */
    const statCard  = { borderRadius:10, padding:'16px 14px',
      display:'flex', flexDirection:'column', gap:2, boxShadow:'0 1px 6px rgba(0,0,0,0.07)' }
    const errBanner = { background:'#fee2e2', color:'#dc2626', borderRadius:8,
      padding:'10px 14px', fontSize:13, marginBottom:12 }
    const okBanner  = { background:'#dcfce7', color:'#16a34a', borderRadius:8,
      padding:'10px 14px', fontSize:13, marginBottom:12 }
    const th     = { textAlign:'left', padding:'8px 12px', background:'#f9fafb',
      color:'#6b7280', fontWeight:600, borderBottom:'1px solid #e5e7eb', fontSize:12 }
    const td     = { padding:'10px 12px', borderBottom:'1px solid #f3f4f6', verticalAlign:'middle' }
    const badge  = { display:'inline-flex', alignItems:'center', gap:4,
      padding:'3px 9px', borderRadius:20, fontSize:11, fontWeight:600 }
    const iconBtn= { background:'none', border:'none', cursor:'pointer', padding:5, borderRadius:6,
      display:'flex', alignItems:'center', justifyContent:'center' }
    const aRow   = { display:'flex', alignItems:'center', gap:10, padding:'10px 12px',
      borderBottom:'1px solid #f3f4f6' }
"""))


print("\n[SmartForest Patch] All done!")
print("""
Next steps:
  1. cd SmartForest-main/frontend
  2. Edit .env and set:
       VITE_API_URL=https://your-render-app.onrender.com/api
  3. npm install   (if not already done)
  4. npm run dev   — test locally

  For Vercel deployment:
    • Go to Vercel → Your Project → Settings → Environment Variables
    • Add:  VITE_API_URL = https://your-render-app.onrender.com/api
    • Redeploy (Deployments → Redeploy) — Vite bakes the URL in at build time.
""")
