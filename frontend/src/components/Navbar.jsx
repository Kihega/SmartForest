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
          {' '}{role === 'admin' ? 'System Admin' : 'Forest Officer'}
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
