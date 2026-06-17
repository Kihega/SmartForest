
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
