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
