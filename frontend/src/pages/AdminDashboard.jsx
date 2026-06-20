
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
          { icon:<Ico paths={I.users} size={22} color="#1b5e20"/>,  label:'Forest Officers', val:customers.length, color:'#1b5e20' },
          { icon:<Ico paths={I.device} size={22} color="#2563eb"/>, label:'Total Devices',   val:devices.length,   color:'#2563eb' },
          { icon:<Ico paths={I.active} size={22} color="#16a34a"/>, label:'Active Devices',  val:activeCount,      color:'#16a34a' },
          { icon:<Ico paths={I.alert} size={22} color="#dc2626"/>,  label:'Open Alerts',     val:count,            color:'#dc2626' },
          { icon:<Ico paths={I.admin} size={22} color="#7c3aed"/>,  label:'System Admins',   val:admins.length,    color:'#7c3aed' },
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
  const [form,   setForm]   = useState({ name:'', email:'', password:'', district:'', role:'officer' })
  const [error,  setError]  = useState('')
  const [ok,     setOk]     = useState('')
  const adminCount = users.filter(u => u.role === 'admin').length

  async function deleteUser(u) {
    if (u.role === 'admin' && adminCount <= 1) { alert('Cannot delete the last System Admin account.'); return }
    const label = u.role === 'admin' ? 'System Admin' : 'Forest Officer'
    if (!confirm(`Delete ${label} ${u.email}?`)) return
    try {
      const api = await getAPI()
      await api.delete(`/admin/users/${u.id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) { alert(err?.response?.data?.error || 'Delete failed.') }
  }

  async function addUser(e) {
    e.preventDefault(); setError(''); setOk('')
    try {
      const api = await getAPI()
      await api.post('/admin/users', form,
        { headers: { Authorization: `Bearer ${session.token}` } })
      setOk(`${form.role === 'admin' ? 'System Admin' : 'Forest Officer'} ${form.email} created.`)
      setForm({ name:'', email:'', password:'', district:'', role:'officer' })
      setAdding(false); onRefresh()
    } catch (err) { setError(err?.response?.data?.error || 'Failed to create user.') }
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
          <Ico paths={I.plus} size={14} color="#fff"/> {adding ? 'Cancel' : 'Add User'}
        </button>
      </div>

      {adding && (
        <div style={{ background:'#f9fef9', border:'1px solid #c8e6c9', borderRadius:8, padding:16, marginBottom:16 }}>
          {error && <div style={errBanner}>{error}</div>}
          {ok    && <div style={okBanner}>{ok}</div>}
          <form onSubmit={addUser} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
            <div>
              <label style={{ fontSize:12, fontWeight:600, display:'block', marginBottom:3 }}>Role</label>
              <select value={form.role} onChange={e => setForm(f => ({ ...f, role:e.target.value }))}
                style={{ width:'100%', padding:'8px 10px', fontSize:13,
                  border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none', background:'#fff' }}>
                <option value="officer">Forest Officer (district level)</option>
                <option value="admin">System Admin (national level)</option>
              </select>
            </div>
            {form.role === 'officer' && (
              <div>
                <label style={{ fontSize:12, fontWeight:600, display:'block', marginBottom:3 }}>District</label>
                <input type="text" value={form.district}
                  onChange={e => setForm(f => ({ ...f, district:e.target.value }))}
                  placeholder="e.g. Kilombero" style={{ width:'100%', padding:'8px 10px', fontSize:13,
                    border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }} />
              </div>
            )}
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
                {form.role === 'admin' ? 'Create System Admin' : 'Register Forest Officer'}
              </button>
            </div>
          </form>
        </div>
      )}

      <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
        <thead><tr>
          {['Name','Email','Role','District','Joined','Actions'].map(h => <th key={h} style={th}>{h}</th>)}
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
                  {u.role === 'admin' ? 'System Admin' : 'Forest Officer'}
                </span>
              </td>
              <td style={{ ...td, fontSize:12 }}>{u.district || '—'}</td>
              <td style={{ ...td, fontSize:11, color:'#9ca3af' }}>
                {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
              </td>
              <td style={td}>
                <button
                  title={u.role==='admin' && adminCount<=1 ? 'Cannot delete last System Admin' : 'Delete user'}
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
