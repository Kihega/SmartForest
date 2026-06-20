import { useState, useEffect, useRef, useCallback } from 'react'
import Navbar  from '../components/Navbar.jsx'
import Sidebar from '../components/Sidebar.jsx'
import ChangePasswordModal from '../components/ChangePasswordModal.jsx'
import { getAPI } from '../services/api.js'

/* ── Leaflet map (OpenStreetMap — free, no API key needed) ── */
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const alertIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="36"><ellipse cx="12" cy="30" rx="6" ry="3" fill="%23c00" opacity=".3"/><path d="M12 0C7.6 0 4 3.6 4 8c0 7 8 22 8 22s8-15 8-22c0-4.4-3.6-8-8-8z" fill="%23e53935"/><circle cx="12" cy="8" r="4" fill="white"/></svg>',
  iconSize:[24,36], iconAnchor:[12,36], popupAnchor:[0,-36],
})
const okIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="36"><ellipse cx="12" cy="30" rx="6" ry="3" fill="%23080" opacity=".3"/><path d="M12 0C7.6 0 4 3.6 4 8c0 7 8 22 8 22s8-15 8-22c0-4.4-3.6-8-8-8z" fill="%232e7d32"/><circle cx="12" cy="8" r="4" fill="white"/></svg>',
  iconSize:[24,36], iconAnchor:[12,36], popupAnchor:[0,-36],
})

const REFRESH_MS = 10_000

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
  alert:    ['M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z','M12 9v4','M12 17h.01'],
  device:   ['M5 12.55a11 11 0 0114.08 0','M1.42 9a16 16 0 0121.16 0','M8.53 16.11a6 6 0 016.95 0','M12 20h.01'],
  fire:     ['M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z'],
  saw:      ['M14.5 4h-5L7 7H4a2 2 0 00-2 2v9a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2h-3z','M10 13a2 2 0 104 0 2 2 0 00-4 0'],
  map:      ['M1 6v16l7-4 8 4 7-4V2l-7 4-8-4z','M8 2v16','M16 6v16'],
  pulse:    ['M22 12h-4l-3 9L9 3l-3 9H2'],
  heart:    ['M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z'],
  mic:      ['M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z','M19 10v2a7 7 0 01-14 0v-2','M12 19v4','M8 23h8'],
  plus:     ['M12 5v14','M5 12h14'],
  trash:    ['M3 6h18','M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a1 1 0 011-1h4a1 1 0 011 1v2'],
  pause:    ['M6 4h4v16H6z','M14 4h4v16h-4z'],
  play:     ['M5 3l14 9-14 9V3z'],
  rangers:  ['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2','M9 7a4 4 0 100 8 4 4 0 000-8z','M19 8v6','M22 11h-6'],
  phone:    ['M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z'],
  pin:      ['M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z','M12 13a3 3 0 100-6 3 3 0 000 6z'],
  team:     ['M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2','M12 7a4 4 0 100 8 4 4 0 000-8z','M22 21v-2a4 4 0 00-3-3.87','M16 3.13a4 4 0 010 7.75'],
  edit:     ['M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7',
             'M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z'],
}

/* ── dot status ── */
function Dot({ on }) {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" style={{ flexShrink:0 }}>
      <circle cx="5" cy="5" r="4.5" fill={on ? '#22c55e' : '#9ca3af'} />
    </svg>
  )
}

const NAV_ITEMS = [
  { id:'home',    iconName:'home',    label:'Home'    },
  { id:'devices', iconName:'devices', label:'Devices' },
  { id:'rangers', iconName:'rangers', label:'Rangers'  },
]

export default function ForestOfficerDashboard({ session, onLogout }) {
  const [page,        setPage]        = useState('home')
  const [mode,        setMode]        = useState('light')
  const [lang,        setLang]        = useState('English')
  const [showPwdModal, setShowPwdModal] = useState(false)

  // data
  const [alerts,  setAlerts]  = useState([])
  const [sensors, setSensors] = useState([])
  const [devices, setDevices] = useState([])
  const [rangers, setRangers] = useState([])
  const [count,   setCount]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  const mountedRef = useRef(true)

  const load = useCallback(async () => {
    try {
      const api = await getAPI()
      const headers = { Authorization: `Bearer ${session.token}` }
      const [a, s, c, d, r] = await Promise.all([
        api.get('/alerts',        { headers }),
        api.get('/sensors/live',  { headers }),
        api.get('/alerts/count',  { headers }),
        api.get('/devices',       { headers }),
        api.get('/rangers',       { headers }),
      ])
      if (!mountedRef.current) return
      setAlerts(a.data  || [])
      setSensors(s.data || [])
      setCount(c.data?.count || 0)
      setDevices(d.data || [])
      setRangers(r.data || [])
      setError('')
    } catch {
      if (mountedRef.current) setError('Could not load data from backend.')
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [session.token])

  useEffect(() => {
    mountedRef.current = true
    load()
    const id = setInterval(load, REFRESH_MS)
    return () => { mountedRef.current = false; clearInterval(id) }
  }, [load])

  function handleNav(id) {
    if (id === 'changepassword') { setShowPwdModal(true); return }
    setPage(id)
  }

  /* apply dark mode CSS variables */
  useEffect(() => {
    const r = document.documentElement
    if (mode === 'dark') {
      r.style.setProperty('--bg',       '#121212')
      r.style.setProperty('--surface',  '#1e1e1e')
      r.style.setProperty('--text',     '#e0e0e0')
      r.style.setProperty('--sub',      '#9e9e9e')
      r.style.setProperty('--border',   '#333')
    } else {
      r.style.setProperty('--bg',       '#f1f8f2')
      r.style.setProperty('--surface',  '#ffffff')
      r.style.setProperty('--text',     '#1b2e1b')
      r.style.setProperty('--sub',      '#6b7280')
      r.style.setProperty('--border',   '#e5e7eb')
    }
  }, [mode])

  const bg      = mode === 'dark' ? '#121212' : '#f1f8f2'
  const surface = mode === 'dark' ? '#1e1e1e' : '#ffffff'
  const text    = mode === 'dark' ? '#e0e0e0' : '#1b2e1b'

  return (
    <div style={{ minHeight:'100vh', background:bg, color:text, fontFamily:"'Segoe UI',system-ui,sans-serif" }}>
      <Navbar session={session} alertCount={count} role="officer" />

      <div style={{ display:'flex' }}>
        <Sidebar
          active={page} onNav={handleNav} onLogout={onLogout}
          mode={mode} onModeChange={setMode}
          lang={lang}  onLangChange={setLang}
          items={NAV_ITEMS}
        />

        <main style={{ flex:1, padding:'24px 28px', maxWidth:1200 }}>
          {error && <div style={errBanner}>{error}</div>}

          {page === 'home'    && <HomePage    alerts={alerts} sensors={sensors} count={count}
                                              loading={loading} surface={surface} text={text} />}
          {page === 'devices' && <DevicesPage devices={devices} alerts={alerts}
                                              session={session} onRefresh={load}
                                              loading={loading} surface={surface} text={text} />}
          {page === 'rangers' && <RangersPage rangers={rangers}
                                              session={session} onRefresh={load}
                                              loading={loading} surface={surface} text={text} />}
        </main>
      </div>

      {showPwdModal && (
        <ChangePasswordModal session={session} onClose={() => setShowPwdModal(false)} />
      )}
    </div>
  )
}

/* ── Home page content ────────────────────────────────────────────────────── */
function HomePage({ alerts, sensors, count, loading, surface, text }) {
  const recentAlerts = alerts.slice(0, 6)
  const mapCenter    = sensors.length
    ? [sensors[0].latitude || -7.78, sensors[0].longitude || 38.95]
    : [-7.78, 38.95]

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* stat cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))', gap:16 }}>
        {[
          { icon:<Ico paths={I.alert} size={22} color="#dc2626"/>, label:'Unresolved Alerts', val:count,         color:'#dc2626' },
          { icon:<Ico paths={I.device} size={22} color="#1b5e20"/>, label:'Active Sensors',    val:sensors.length, color:'#1b5e20' },
          { icon:<Ico paths={I.fire} size={22} color="#f57c00"/>, label:'Fire Alerts',
            val: alerts.filter(a=>a.alert_type==='fire').length,        color:'#f57c00' },
          { icon:<Ico paths={I.saw} size={22} color="#92400e"/>, label:'Logging Alerts',
            val: alerts.filter(a=>a.alert_type==='illegal_logging').length, color:'#5c3317' },
        ].map(c => (
          <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
            {c.icon}
            <span style={{ fontSize:12, opacity:0.7, marginTop:4 }}>{c.label}</span>
            <span style={{ fontSize:28, fontWeight:800, color:c.color }}>
              {loading ? '…' : c.val}
            </span>
          </div>
        ))}
      </div>

      {/* live map */}
      <Section title="Live Device Map" icon={<Ico paths={I.map} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <div style={{ height:340, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {sensors.map(s => s.latitude && (
              <Marker key={s.id} position={[s.latitude, s.longitude]}
                icon={s.is_alert ? alertIcon : okIcon}>
                <Popup>
                  <strong>{s.device_id}</strong><br/>
                  Zone: {s.zone}<br/>
                  Status: {s.is_alert ? 'Alert' : 'Normal'}<br/>
                  {s.sensor_type === 'microphone'
                    ? `Sound: ${s.sound_db} dB`
                    : `Temp: ${s.temperature_c}°C`}
                </Popup>
                {s.is_alert && <Circle center={[s.latitude, s.longitude]}
                  radius={500} color="#e53935" fillOpacity={0.12} />}
              </Marker>
            ))}
          </MapContainer>
        </div>
        <p style={{ fontSize:11, color:'#888', marginTop:4 }}>
          Map: OpenStreetMap (free, no API key) · Red = alert · Green = normal
        </p>
      </Section>

      {/* live alert trends */}
      <Section title="Live Alert Trends" icon={<Ico paths={I.pulse} size={16} color="#6b7280"/>} surface={surface} text={text}>
        {recentAlerts.length === 0
          ? <Empty>No alerts yet — all sensors reporting normal.</Empty>
          : (
            <div style={{ display:'grid', gap:8 }}>
              {recentAlerts.map(a => (
                <AlertRow key={a.id} alert={a} />
              ))}
              {alerts.length > 6 && (
                <p style={{ fontSize:12, color:'#888', textAlign:'right' }}>
                  Showing 6 of {alerts.length} alerts
                </p>
              )}
            </div>
          )}
      </Section>

      {/* system health summary */}
      <Section title="System Health" icon={<Ico paths={I.heart} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
          <HealthItem label="Microphone sensors" val={sensors.filter(s=>s.sensor_type==='microphone').length} />
          <HealthItem label="Flame sensors"      val={sensors.filter(s=>s.sensor_type==='flame').length} />
          <HealthItem label="Total alerts"       val={alerts.length} />
          <HealthItem label="Resolved"
            val={alerts.filter(a=>a.status==='resolved').length} good />
        </div>
      </Section>
    </div>
  )
}

/* ── Devices page ─────────────────────────────────────────────────────────── */
function DevicesPage({ devices, alerts, session, onRefresh, loading, surface, text }) {
  const [addId,    setAddId]    = useState('')
  const [addZone,  setAddZone]  = useState('')
  const [addError, setAddError] = useState('')
  const [addOk,    setAddOk]    = useState('')
  const [busy,     setBusy]     = useState(false)
  const [search,   setSearch]   = useState('')

  const recentAlerts = alerts.slice(0, 6)
  const filtered = devices.filter(d =>
    d.device_id?.toLowerCase().includes(search.toLowerCase()) ||
    (d.zone || '').toLowerCase().includes(search.toLowerCase())
  )

  async function addDevice(e) {
    e.preventDefault()
    setAddError(''); setAddOk('')
    if (!addId.trim()) { setAddError('Device ID is required.'); return }
    setBusy(true)
    try {
      const api = await getAPI()
      await api.post('/devices', { device_id: addId.trim(), zone: addZone.trim() || undefined },
        { headers: { Authorization: `Bearer ${session.token}` } })
      setAddOk(`Device ${addId.trim()} registered successfully.`)
      setAddId(''); setAddZone('')
      onRefresh()
    } catch (err) {
      setAddError(err?.response?.data?.error || 'Failed to register device.')
    } finally {
      setBusy(false)
    }
  }

  async function removeDevice(id) {
    if (!confirm(`Delete device ${id}? This removes all related data.`)) return
    try {
      const api = await getAPI()
      await api.delete(`/devices/${id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Delete failed.')
    }
  }

  async function suspendDevice(id, active) {
    try {
      const api = await getAPI()
      await api.patch(`/devices/${id}/status`,
        { active: !active },
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Update failed.')
    }
  }

  const mapCenter = devices.length && devices[0].latitude
    ? [devices[0].latitude, devices[0].longitude]
    : [-7.78, 38.95]

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* live device map */}
      <Section title="Live Device Deployment" icon={<Ico paths={I.map} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <div style={{ height:300, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'/>
            {devices.map(d => d.latitude && (
              <Marker key={d.id} position={[d.latitude, d.longitude]}
                icon={d.active ? okIcon : alertIcon}>
                <Popup>
                  <strong>{d.device_id}</strong><br/>
                  Status: {d.active ? 'Active' : 'Suspended'}<br/>
                  Mount location: {d.zone || '—'}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </Section>

      {/* live alerts */}
      <Section title="Recent Alerts" icon={<Ico paths={I.alert} size={16} color="#6b7280"/>} surface={surface} text={text}>
        {recentAlerts.length === 0
          ? <Empty>No alerts yet.</Empty>
          : recentAlerts.map(a => <AlertRow key={a.id} alert={a} />)}
      </Section>

      {/* add device */}
      <Section title="Register New Device" icon={<Ico paths={I.plus} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <p style={{ fontSize:13, color:'#666', marginBottom:12 }}>
          Enter the device ID and mount location (e.g. <code>smf-01a</code> at
          "Kilombero District — Sector 4").
        </p>
        {addError && <div style={errBanner}>{addError}</div>}
        {addOk    && <div style={okBanner}>{addOk}</div>}
        <form onSubmit={addDevice} style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
          <input
            data-testid="device-id-input"
            placeholder="Device ID (e.g. smf-01a)"
            value={addId}
            onChange={e => setAddId(e.target.value)}
            style={{ flex:'1 1 180px', padding:'9px 12px', fontSize:13,
              border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }}
          />
          <input
            data-testid="device-zone-input"
            placeholder="Mount location (e.g. Kilombero - Sector 4)"
            value={addZone}
            onChange={e => setAddZone(e.target.value)}
            style={{ flex:'1 1 240px', padding:'9px 12px', fontSize:13,
              border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }}
          />
          <button type="submit" disabled={busy}
            style={{ padding:'9px 20px', background:'#2e7d32', color:'#fff',
              border:'none', borderRadius:7, fontWeight:700, cursor:'pointer',
              opacity: busy ? 0.7 : 1 }}>
            {busy ? 'Adding…' : 'Add Device'}
          </button>
        </form>
      </Section>

      {/* registered devices list — searchable by id or mount location */}
      <Section title="Registered Devices" icon={<Ico paths={I.device} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <div style={{ position:'relative', marginBottom:14, maxWidth:340 }}>
          <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)' }}>
            <Ico paths={['M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0']} size={14} color="#9ca3af"/>
          </span>
          <input
            type="text" placeholder="Filter by device ID or location…"
            value={search} onChange={e => setSearch(e.target.value)}
            style={{ width:'100%', padding:'8px 10px 8px 32px', fontSize:13,
              border:'1.5px solid #e5e7eb', borderRadius:8, outline:'none' }}
          />
        </div>
        {loading
          ? <Empty>Loading…</Empty>
          : filtered.length === 0
            ? <Empty>{devices.length === 0 ? 'No devices registered yet. Add your first device above.' : 'No devices match your filter.'}</Empty>
            : (
              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
                <thead>
                  <tr>{['Device ID','Mount Location','Status','Last Seen','Actions'].map(h =>
                    <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {filtered.map(d => (
                    <tr key={d.id}>
                      <td style={td}><strong>{d.device_id}</strong></td>
                      <td style={td}>{d.zone || '—'}</td>
                      <td style={td}>
                        <span style={d.active
                          ? { ...badge, background:'#e8f5e9', color:'#2e7d32' }
                          : { ...badge, background:'#fafafa', color:'#888' }}>
                          <Dot on={d.active}/> {d.active ? 'Active' : 'Suspended'}
                        </span>
                      </td>
                      <td style={{ ...td, color:'#888', fontSize:11 }}>
                        {d.last_seen ? new Date(d.last_seen).toLocaleString() : '—'}
                      </td>
                      <td style={td}>
                        <div style={{ display:'flex', gap:8 }}>
                          <button
                            title={d.active ? 'Suspend device (stops data stream)' : 'Resume device'}
                            onClick={() => suspendDevice(d.device_id, d.active)}
                            style={{ ...iconBtn, color: d.active ? '#f57c00' : '#2e7d32' }}>
                            <Ico paths={d.active ? I.pause : I.play} size={15} color="currentColor"/>
                          </button>
                          <button
                            title="Delete device (removes all data)"
                            onClick={() => removeDevice(d.device_id)}
                            style={{ ...iconBtn, color:'#e53935' }}>
                            <Ico paths={I.trash} size={15} color="currentColor"/>
                          </button>
                        </div>
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

/* ── Forest Rangers page — SMS-only field staff, no login ─────────────────── */
function RangersPage({ rangers, session, onRefresh, loading, surface, text }) {
  const [adding,   setAdding]   = useState(false)
  const [editing,  setEditing]  = useState(null) // ranger id being edited, or null
  const [form,     setForm]     = useState(emptyRangerForm())
  const [error,    setError]    = useState('')
  const [ok,       setOk]       = useState('')
  const [search,   setSearch]   = useState('')
  const [busy,     setBusy]     = useState(false)

  function emptyRangerForm() {
    return { full_name:'', phone:'', location:'', team_id:'', role:'team_member' }
  }

  function startEdit(r) {
    setEditing(r.id)
    setForm({ full_name:r.full_name, phone:r.phone, location:r.location || '',
      team_id:r.team_id || '', role:r.role || 'team_member' })
    setAdding(true)
  }

  function cancelForm() {
    setAdding(false); setEditing(null); setForm(emptyRangerForm()); setError(''); setOk('')
  }

  async function submitForm(e) {
    e.preventDefault()
    setError(''); setOk(''); setBusy(true)
    try {
      const api = await getAPI()
      const headers = { Authorization: `Bearer ${session.token}` }
      if (editing) {
        await api.patch(`/rangers/${editing}`, form, { headers })
        setOk(`Ranger ${form.full_name} updated.`)
      } else {
        await api.post('/rangers', form, { headers })
        setOk(`Ranger ${form.full_name} registered.`)
      }
      cancelForm()
      onRefresh()
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to save ranger.')
    } finally {
      setBusy(false)
    }
  }

  async function removeRanger(r) {
    if (!confirm(`Remove Forest Ranger ${r.full_name}?`)) return
    try {
      const api = await getAPI()
      await api.delete(`/rangers/${r.id}`,
        { headers: { Authorization: `Bearer ${session.token}` } })
      onRefresh()
    } catch (err) {
      alert(err?.response?.data?.error || 'Delete failed.')
    }
  }

  const filtered = rangers.filter(r =>
    r.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    r.phone?.includes(search) ||
    (r.location || '').toLowerCase().includes(search.toLowerCase()) ||
    (r.team_id  || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ display:'grid', gap:24 }}>
      {/* summary cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))', gap:14 }}>
        {[
          { label:'Total Rangers', val:rangers.length, icon:<Ico paths={I.rangers} size={22} color="#1b5e20"/>, color:'#1b5e20' },
          { label:'Team Leads',    val:rangers.filter(r=>r.role==='team_lead').length, icon:<Ico paths={I.team} size={22} color="#7c3aed"/>, color:'#7c3aed' },
          { label:'Team Members',  val:rangers.filter(r=>r.role!=='team_lead').length, icon:<Ico paths={I.team} size={22} color="#2563eb"/>, color:'#2563eb' },
        ].map(c => (
          <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
            {c.icon}
            <span style={{ fontSize:11, opacity:0.65, marginTop:4 }}>{c.label}</span>
            <span style={{ fontSize:26, fontWeight:800, color:c.color }}>
              {loading ? '…' : c.val}
            </span>
          </div>
        ))}
      </div>

      {/* explainer */}
      <div style={{ background:'#f1f8f2', border:'1px solid #c8e6c9', borderRadius:10,
        padding:'12px 16px', fontSize:12.5, color:'#33543c', display:'flex', gap:10 }}>
        <Ico paths={I.phone} size={18} color="#2e7d32"/>
        <div>
          Forest Rangers are SMS-only field staff and do not log into this dashboard.
          Their device's GSM module sends them SMS alerts directly. If an SMS isn't
          delivered, use the phone number below to call them as a manual backup.
        </div>
      </div>

      <Section title={editing ? 'Edit Forest Ranger' : 'Register Forest Ranger'}
        icon={<Ico paths={I.plus} size={16} color="#6b7280"/>} surface={surface} text={text}
        headerRight={
          <button onClick={() => adding ? cancelForm() : setAdding(true)}
            style={{ display:'flex', alignItems:'center', gap:5,
              padding:'7px 16px', background:'#2e7d32', color:'#fff',
              border:'none', borderRadius:7, fontWeight:700, cursor:'pointer', fontSize:13 }}>
            <Ico paths={I.plus} size={14} color="#fff"/> {adding ? 'Cancel' : 'Add Ranger'}
          </button>
        }>
        {adding && (
          <div style={{ background:'#f9fef9', border:'1px solid #c8e6c9', borderRadius:8, padding:16 }}>
            {error && <div style={errBanner}>{error}</div>}
            {ok    && <div style={okBanner}>{ok}</div>}
            <form onSubmit={submitForm} style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              <div>
                <label style={lbl}>Full Name</label>
                <input type="text" required value={form.full_name}
                  onChange={e => setForm(f => ({ ...f, full_name:e.target.value }))}
                  style={inp} />
              </div>
              <div>
                <label style={lbl}>Phone Number</label>
                <input type="tel" required value={form.phone}
                  placeholder="+255 7xx xxx xxx"
                  onChange={e => setForm(f => ({ ...f, phone:e.target.value }))}
                  style={inp} />
              </div>
              <div>
                <label style={lbl}>Location</label>
                <input type="text" value={form.location}
                  placeholder="e.g. Kilombero - Sector 4"
                  onChange={e => setForm(f => ({ ...f, location:e.target.value }))}
                  style={inp} />
              </div>
              <div>
                <label style={lbl}>Team ID</label>
                <input type="text" value={form.team_id}
                  placeholder="e.g. A, B, C"
                  onChange={e => setForm(f => ({ ...f, team_id:e.target.value }))}
                  style={inp} />
              </div>
              <div style={{ gridColumn:'1/-1' }}>
                <label style={lbl}>Role</label>
                <select value={form.role}
                  onChange={e => setForm(f => ({ ...f, role:e.target.value }))}
                  style={{ ...inp, background:'#fff' }}>
                  <option value="team_member">Team Member</option>
                  <option value="team_lead">Team Lead</option>
                </select>
              </div>
              <div style={{ gridColumn:'1/-1' }}>
                <button type="submit" disabled={busy} style={{ padding:'8px 20px', background:'#1b5e20',
                  color:'#fff', border:'none', borderRadius:7, fontWeight:700, cursor:'pointer',
                  opacity: busy ? 0.7 : 1 }}>
                  {busy ? 'Saving…' : editing ? 'Save Changes' : 'Register Ranger'}
                </button>
              </div>
            </form>
          </div>
        )}
      </Section>

      <Section title="All Forest Rangers" icon={<Ico paths={I.rangers} size={16} color="#6b7280"/>} surface={surface} text={text}>
        <div style={{ position:'relative', marginBottom:14, maxWidth:340 }}>
          <span style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)' }}>
            <Ico paths={['M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0']} size={14} color="#9ca3af"/>
          </span>
          <input
            type="text" placeholder="Filter by name, phone, location or team…"
            value={search} onChange={e => setSearch(e.target.value)}
            style={{ width:'100%', padding:'8px 10px 8px 32px', fontSize:13,
              border:'1.5px solid #e5e7eb', borderRadius:8, outline:'none' }}
          />
        </div>

        {loading
          ? <Empty>Loading…</Empty>
          : filtered.length === 0
            ? <Empty>{rangers.length === 0 ? 'No Forest Rangers registered yet.' : 'No rangers match your filter.'}</Empty>
            : (
              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
                <thead><tr>
                  {['Name','Phone','Location','Team','Role','Actions'].map(h => <th key={h} style={th}>{h}</th>)}
                </tr></thead>
                <tbody>
                  {filtered.map(r => (
                    <tr key={r.id}>
                      <td style={td}><strong>{r.full_name}</strong></td>
                      <td style={td}>
                        <span style={{ display:'flex', alignItems:'center', gap:5 }}>
                          <Ico paths={I.phone} size={13} color="#2e7d32"/> {r.phone}
                        </span>
                      </td>
                      <td style={td}>
                        <span style={{ display:'flex', alignItems:'center', gap:5 }}>
                          <Ico paths={I.pin} size={13} color="#9ca3af"/> {r.location || '—'}
                        </span>
                      </td>
                      <td style={td}>{r.team_id || '—'}</td>
                      <td style={td}>
                        <span style={r.role==='team_lead'
                          ? { ...badge, background:'#ede9fe', color:'#7c3aed' }
                          : { ...badge, background:'#dbeafe', color:'#1d4ed8' }}>
                          {r.role === 'team_lead' ? 'Team Lead' : 'Team Member'}
                        </span>
                      </td>
                      <td style={td}>
                        <div style={{ display:'flex', gap:8 }}>
                          <button title="Edit ranger" onClick={() => startEdit(r)}
                            style={{ ...iconBtn, color:'#2563eb' }}>
                            <Ico paths={I.edit} size={14} color="currentColor"/>
                          </button>
                          <button title="Remove ranger" onClick={() => removeRanger(r)}
                            style={{ ...iconBtn, color:'#dc2626' }}>
                            <Ico paths={I.trash} size={14} color="currentColor"/>
                          </button>
                        </div>
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

/* ── small shared components ─────────────────────────────────────────────── */
function Section({ title, icon, children, surface, text, headerRight }) {
  return (
    <div style={{ background:surface, borderRadius:12, padding:'20px 22px',
      boxShadow:'0 1px 6px rgba(0,0,0,0.08)', color:text }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, fontSize:15, fontWeight:700 }}>
          {icon} {title}
        </div>
        {headerRight}
      </div>
      {children}
    </div>
  )
}

function AlertRow({ alert: a }) {
  const isLog = a.alert_type === 'illegal_logging'
  return (
    <div style={{ display:'flex', alignItems:'center', gap:12,
      padding:'10px 14px', borderRadius:8,
      background: isLog ? '#fff8e1' : '#ffebee',
      border:`1px solid ${isLog ? '#ffe082' : '#ffcdd2'}` }}>
      <Ico paths={isLog ? I.saw : I.fire} size={20} color={isLog ? '#92400e' : '#dc2626'} />
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontWeight:700, fontSize:13 }}>
          {isLog ? 'Illegal Logging' : 'Fire Detected'} — {a.device_id}
        </div>
        <div style={{ fontSize:11, color:'#888' }}>
          {a.zone} · {a.sensor_type === 'microphone'
            ? `${a.sound_db} dB` : `${a.temperature_c}°C`}
        </div>
      </div>
      <div style={{ fontSize:11, color:'#aaa', whiteSpace:'nowrap' }}>
        {new Date(a.created_at).toLocaleString()}
      </div>
      <span style={{ ...badge,
        background: a.status==='resolved' ? '#e8f5e9' : '#ffebee',
        color:       a.status==='resolved' ? '#2e7d32' : '#c62828' }}>
        {a.status}
      </span>
    </div>
  )
}

function HealthItem({ label, val, good }) {
  return (
    <div style={{ padding:'12px 16px', borderRadius:8,
      background: good ? '#e8f5e9' : '#f5f5f5',
      display:'flex', justifyContent:'space-between', alignItems:'center' }}>
      <span style={{ fontSize:13, color:'#555' }}>{label}</span>
      <span style={{ fontSize:20, fontWeight:800, color: good ? '#2e7d32' : '#333' }}>{val}</span>
    </div>
  )
}

function Empty({ children }) {
  return <div style={{ textAlign:'center', padding:'32px', color:'#aaa', fontSize:13 }}>{children}</div>
}

/* ── style tokens ──────────────────────────────────────────────────────────  */
const statCard = { borderRadius:10, padding:'18px 16px',
  display:'flex', flexDirection:'column', gap:4,
  boxShadow:'0 1px 6px rgba(0,0,0,0.07)' }
const errBanner = { background:'#ffebee', color:'#c62828', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const okBanner  = { background:'#e8f5e9', color:'#1b5e20', borderRadius:8,
  padding:'10px 14px', fontSize:13, marginBottom:12 }
const th   = { textAlign:'left', padding:'8px 12px',
  background:'#f9fafb', color:'#6b7280', fontWeight:600,
  borderBottom:'1px solid #e5e7eb', fontSize:12 }
const td   = { padding:'10px 12px', borderBottom:'1px solid #f3f4f6', verticalAlign:'middle' }
const badge= { display:'inline-flex', alignItems:'center', gap:4, padding:'3px 9px',
  borderRadius:20, fontSize:11, fontWeight:600 }
const iconBtn = { background:'none', border:'none', cursor:'pointer',
  padding:5, borderRadius:6, display:'flex', alignItems:'center', justifyContent:'center' }
const lbl = { fontSize:12, fontWeight:600, display:'block', marginBottom:3 }
const inp = { width:'100%', padding:'8px 10px', fontSize:13,
  border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }
