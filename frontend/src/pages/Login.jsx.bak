
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
      const reason = err?.response?.data?.reason
      const serverMsg = err?.response?.data?.error
      if (err?.message === 'NO_BACKEND') {
        setError('Cannot reach any backend server. Check your internet connection or try again shortly.')
      } else if (reason === 'invalid_credentials') {
        setError(serverMsg || 'Incorrect email or password.')
      } else if (reason === 'supabase_unreachable') {
        setError('Authentication service is temporarily unavailable. Please try again in a moment.')
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
