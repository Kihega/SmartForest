import Navbar from '../components/Navbar.jsx'

const S = {
  page:    { minHeight:'100vh', background:'#f9fafb' },
  content: { maxWidth:1100, margin:'0 auto', padding:'32px 20px' },
  grid:    { display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))',
             gap:16, marginBottom:32 },
  card: {
    background:'#fff', borderRadius:10, padding:'24px 20px',
    boxShadow:'0 1px 4px rgba(0,0,0,0.08)'
  },
  cardIcon: { fontSize:28, marginBottom:10 },
  cardTitle:{ fontSize:14, color:'#6b7280', marginBottom:4 },
  cardVal:  { fontSize:28, fontWeight:700, color:'#111827' },
  section:  {
    background:'#fff', borderRadius:10, padding:'24px',
    boxShadow:'0 1px 4px rgba(0,0,0,0.08)', marginBottom:20
  },
  secTitle: { fontSize:16, fontWeight:700, color:'#111827', marginBottom:16 },
  badge: {
    display:'inline-block', padding:'4px 10px', borderRadius:20,
    fontSize:12, fontWeight:600
  },
  row: {
    display:'flex', alignItems:'center', gap:12,
    padding:'12px 0', borderBottom:'1px solid #f3f4f6'
  },
  comingSoon: {
    textAlign:'center', padding:'40px 20px',
    color:'#9ca3af', fontSize:14
  }
}

const PANELS = [
  { icon:'📡', title:'Device Management',
    desc:'Register sensors, assign zones, manage MIC and FLAME devices' },
  { icon:'👥', title:'User Management',
    desc:'Create ranger accounts, assign devices, set roles and permissions' },
  { icon:'⚙️', title:'System Settings',
    desc:'Alert thresholds, deduplication windows, MQTT broker config' },
  { icon:'📊', title:'System Reports',
    desc:'Full audit logs, all zones, all devices — export CSV' },
]

export default function AdminDashboard({ session, onLogout }) {
  return (
    <div style={S.page}>
      <Navbar session={session} onLogout={onLogout} role="admin" />

      <div style={S.content}>

        {/* Stats row */}
        <div style={S.grid}>
          {[
            { icon:'📡', label:'Total Devices',    val:'—' },
            { icon:'👥', label:'Registered Users', val:'—' },
            { icon:'🚨', label:'Active Alerts',    val:'—' },
            { icon:'✅', label:'Resolved Today',   val:'—' },
          ].map(c => (
            <div key={c.label} style={S.card}>
              <div style={S.cardIcon}>{c.icon}</div>
              <div style={S.cardTitle}>{c.label}</div>
              <div style={S.cardVal}>{c.val}</div>
            </div>
          ))}
        </div>

        {/* Admin panels */}
        <div style={S.grid}>
          {PANELS.map(p => (
            <div key={p.title} style={S.section}>
              <div style={{fontSize:32,marginBottom:10}}>{p.icon}</div>
              <div style={S.secTitle}>{p.title}</div>
              <p style={{fontSize:13,color:'#6b7280',marginBottom:16}}>{p.desc}</p>
              <div style={S.comingSoon}>
                🔧 Coming in next sprint
              </div>
            </div>
          ))}
        </div>

        {/* Recent activity placeholder */}
        <div style={S.section}>
          <div style={S.secTitle}>🕐 Recent System Activity</div>
          {['MQTT broker connected','Sensor MIC-001 registered',
            'Alert threshold set to 80dB'].map((item,i) => (
            <div key={i} style={S.row}>
              <span style={{...S.badge,background:'#f0fdf4',color:'#16a34a'}}>INFO</span>
              <span style={{fontSize:13,color:'#374151'}}>{item}</span>
            </div>
          ))}
          <div style={S.comingSoon}>Live activity feed — Sprint 4</div>
        </div>

      </div>
    </div>
  )
}
