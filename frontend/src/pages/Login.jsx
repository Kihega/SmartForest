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
