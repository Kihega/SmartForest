const S = {
  nav: {
    background:'#14532d', color:'#fff',
    display:'flex', alignItems:'center',
    justifyContent:'space-between',
    padding:'0 24px', height:56,
    boxShadow:'0 2px 8px rgba(0,0,0,0.2)'
  },
  left:  { display:'flex', alignItems:'center', gap:10 },
  logo:  { fontSize:20 },
  title: { fontSize:16, fontWeight:700, letterSpacing:0.3 },
  right: { display:'flex', alignItems:'center', gap:14 },
  badge: {
    background:'#dc2626', color:'#fff',
    borderRadius:20, padding:'2px 8px',
    fontSize:12, fontWeight:700
  },
  roleTag: {
    background:'rgba(255,255,255,0.15)',
    borderRadius:20, padding:'3px 10px',
    fontSize:12, fontWeight:600
  },
  user:  { fontSize:13, opacity:0.85 },
  btn: {
    background:'rgba(255,255,255,0.15)',
    color:'#fff', padding:'6px 14px',
    borderRadius:6, fontSize:13, fontWeight:600
  }
}

export default function Navbar({ session, onLogout, alertCount, role }) {
  return (
    <nav style={S.nav}>
      <div style={S.left}>
        <span style={S.logo}>🌿</span>
        <span style={S.title}>SmartForest</span>
        <span style={S.roleTag}>
          {role === 'admin' ? '⚙️ Admin' : '👤 User'}
        </span>
      </div>
      <div style={S.right}>
        {alertCount > 0 && (
          <span style={S.badge}>🚨 {alertCount} alert{alertCount !== 1 ? 's' : ''}</span>
        )}
        <span style={S.user}>
          {session?.user?.name || session?.user?.email || 'User'}
        </span>
        <button style={S.btn} onClick={onLogout}>Sign out</button>
      </div>
    </nav>
  )
}
