import { useState, useEffect, useRef, useCallback } from 'react'
import Navbar  from '../components/Navbar.jsx'
import Sidebar from '../components/Sidebar.jsx'
import ChangePasswordModal from '../components/ChangePasswordModal.jsx'
import { getAPI } from '../services/api.js'

/* ── Leaflet map (OpenStreetMap — free, no API key needed) ─────────────────
   We use react-leaflet which is already in package.json.
   Google Maps would require: npm i @react-google-maps/api  and a paid API key.
   OpenStreetMap / Leaflet is the recommended free alternative.               */
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix leaflet default icon path issue with Vite
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

export default function UserDashboard({ session, onLogout }) {
  const [page,        setPage]        = useState('home')
  const [mode,        setMode]        = useState('light')
  const [lang,        setLang]        = useState('English')
  const [showPwdModal, setShowPwdModal] = useState(false)

  // data
  const [alerts,  setAlerts]  = useState([])
  const [sensors, setSensors] = useState([])
  const [devices, setDevices] = useState([])
  const [count,   setCount]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  const mountedRef = useRef(true)

  const load = useCallback(async () => {
    try {
      const api = await getAPI()
      const headers = { Authorization: `Bearer ${session.token}` }
      const [a, s, c, d] = await Promise.all([
        api.get('/alerts',        { headers }),
        api.get('/sensors/live',  { headers }),
        api.get('/alerts/count',  { headers }),
        api.get('/devices',       { headers }),
      ])
      if (!mountedRef.current) return
      setAlerts(a.data  || [])
      setSensors(s.data || [])
      setCount(c.data?.count || 0)
      setDevices(d.data || [])
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
      <Navbar session={session} alertCount={count} role="user" />

      <div style={{ display:'flex' }}>
        <Sidebar
          active={page} onNav={handleNav} onLogout={onLogout}
          mode={mode} onModeChange={setMode}
          lang={lang}  onLangChange={setLang}
        />

        <main style={{ flex:1, padding:'24px 28px', maxWidth:1200 }}>
          {error && <div style={errBanner}>{error}</div>}

          {page === 'home'    && <HomePage    alerts={alerts} sensors={sensors} count={count}
                                              loading={loading} surface={surface} text={text} />}
          {page === 'devices' && <DevicesPage devices={devices} alerts={alerts}
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
          { icon:'🚨', label:'Unresolved Alerts', val:count,         color:'#e53935' },
          { icon:'📡', label:'Active Sensors',    val:sensors.length, color:'#1b5e20' },
          { icon:'🔥', label:'Fire Alerts',
            val: alerts.filter(a=>a.alert_type==='fire').length,        color:'#f57c00' },
          { icon:'🪚', label:'Logging Alerts',
            val: alerts.filter(a=>a.alert_type==='illegal_logging').length, color:'#5c3317' },
        ].map(c => (
          <div key={c.label} style={{ ...statCard, background:surface, color:text }}>
            <span style={{ fontSize:28 }}>{c.icon}</span>
            <span style={{ fontSize:12, opacity:0.7 }}>{c.label}</span>
            <span style={{ fontSize:28, fontWeight:800, color:c.color }}>
              {loading ? '…' : c.val}
            </span>
          </div>
        ))}
      </div>

      {/* live map */}
      <Section title="🗺 Live Device Map" surface={surface} text={text}>
        <div style={{ height:340, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            {sensors.map(s => s.latitude && (
              <Marker key={s.id} position={[s.latitude, s.longitude]}
                icon={s.is_alert ? alertIcon : okIcon}>
                <Popup>
                  <strong>{s.device_id}</strong><br/>
                  Zone: {s.zone}<br/>
                  Status: {s.is_alert ? '🔴 Alert' : '🟢 Normal'}<br/>
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
      <Section title="⚡ Live Alert Trends" surface={surface} text={text}>
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
      <Section title="💚 System Health" surface={surface} text={text}>
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
  const [addError, setAddError] = useState('')
  const [addOk,    setAddOk]    = useState('')
  const [busy,     setBusy]     = useState(false)

  const recentAlerts = alerts.slice(0, 6)

  async function addDevice(e) {
    e.preventDefault()
    setAddError(''); setAddOk('')
    if (!addId.trim()) { setAddError('Device ID is required.'); return }
    setBusy(true)
    try {
      const api = await getAPI()
      await api.post('/devices', { device_id: addId.trim() },
        { headers: { Authorization: `Bearer ${session.token}` } })
      setAddOk(`Device ${addId.trim()} registered successfully.`)
      setAddId('')
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
      <Section title="🗺 Live Device Deployment" surface={surface} text={text}>
        <div style={{ height:300, borderRadius:8, overflow:'hidden', border:'1px solid #c8e6c9' }}>
          <MapContainer center={mapCenter} zoom={11} style={{ height:'100%', width:'100%' }}
            scrollWheelZoom={false}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© OpenStreetMap contributors'/>
            {devices.map(d => d.latitude && (
              <Marker key={d.id} position={[d.latitude, d.longitude]}
                icon={d.active ? okIcon : alertIcon}>
                <Popup>
                  <strong>{d.device_id}</strong><br/>
                  Status: {d.active ? '🟢 Active' : '⭕ Suspended'}<br/>
                  Zone: {d.zone || '—'}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </Section>

      {/* live alerts */}
      <Section title="⚡ Recent Alerts" surface={surface} text={text}>
        {recentAlerts.length === 0
          ? <Empty>No alerts yet.</Empty>
          : recentAlerts.map(a => <AlertRow key={a.id} alert={a} />)}
      </Section>

      {/* add device */}
      <Section title="➕ Register New Device" surface={surface} text={text}>
        <p style={{ fontSize:13, color:'#666', marginBottom:12 }}>
          Enter the hardware ID printed on your device (e.g. <code>smf-01a</code> for real hardware
          or <code>smt-01a</code> for simulator units).
        </p>
        {addError && <div style={errBanner}>{addError}</div>}
        {addOk    && <div style={okBanner}>{addOk}</div>}
        <form onSubmit={addDevice} style={{ display:'flex', gap:10 }}>
          <input
            data-testid="device-id-input"
            placeholder="Device ID (e.g. smf-01a)"
            value={addId}
            onChange={e => setAddId(e.target.value)}
            style={{ flex:1, padding:'9px 12px', fontSize:13,
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

      {/* registered devices list */}
      <Section title="📋 Registered Devices" surface={surface} text={text}>
        {loading
          ? <Empty>Loading…</Empty>
          : devices.length === 0
            ? <Empty>No devices registered yet. Add your first device above.</Empty>
            : (
              <table style={{ width:'100%', borderCollapse:'collapse', fontSize:13 }}>
                <thead>
                  <tr>{['Device ID','Zone','Status','Last Seen','Actions'].map(h =>
                    <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {devices.map(d => (
                    <tr key={d.id}>
                      <td style={td}><strong>{d.device_id}</strong></td>
                      <td style={td}>{d.zone || '—'}</td>
                      <td style={td}>
                        <span style={d.active
                          ? { ...badge, background:'#e8f5e9', color:'#2e7d32' }
                          : { ...badge, background:'#fafafa', color:'#888' }}>
                          {d.active ? '🟢 Active' : '⭕ Suspended'}
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
                            {d.active ? '⏸' : '▶'}
                          </button>
                          <button
                            title="Delete device (removes all data)"
                            onClick={() => removeDevice(d.device_id)}
                            style={{ ...iconBtn, color:'#e53935' }}>
                            🗑
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
function Section({ title, children, surface, text }) {
  return (
    <div style={{ background:surface, borderRadius:12, padding:'20px 22px',
      boxShadow:'0 1px 6px rgba(0,0,0,0.08)', color:text }}>
      <div style={{ fontSize:15, fontWeight:700, marginBottom:14 }}>{title}</div>
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
      <span style={{ fontSize:22 }}>{isLog ? '🪚' : '🔥'}</span>
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
const badge= { display:'inline-block', padding:'3px 9px',
  borderRadius:20, fontSize:11, fontWeight:600 }
const iconBtn = { background:'none', border:'none', cursor:'pointer',
  fontSize:18, padding:4, borderRadius:6 }
