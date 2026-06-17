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
