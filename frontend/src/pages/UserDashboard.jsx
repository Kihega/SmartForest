import { useState, useEffect, useCallback } from 'react'
import Navbar from '../components/Navbar.jsx'
import { getAPI } from '../services/api.js'

const S = {
  page:    { minHeight:'100vh', background:'#f9fafb' },
  content: { maxWidth:1100, margin:'0 auto', padding:'32px 20px' },
  grid:    { display:'grid',
             gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',
             gap:16, marginBottom:28 },
  card: {
    background:'#fff', borderRadius:10, padding:'22px 18px',
    boxShadow:'0 1px 4px rgba(0,0,0,0.08)'
  },
  cardIcon:  { fontSize:26, marginBottom:8 },
  cardLabel: { fontSize:13, color:'#6b7280', marginBottom:4 },
  cardVal:   { fontSize:26, fontWeight:700 },
  section: {
    background:'#fff', borderRadius:10, padding:'22px',
    boxShadow:'0 1px 4px rgba(0,0,0,0.08)', marginBottom:20
  },
  secTitle: { fontSize:15, fontWeight:700, color:'#111827', marginBottom:14 },
  table:    { width:'100%', borderCollapse:'collapse', fontSize:13 },
  th: {
    textAlign:'left', padding:'8px 10px',
    background:'#f9fafb', color:'#6b7280',
    fontWeight:600, borderBottom:'1px solid #e5e7eb'
  },
  td: {
    padding:'10px', borderBottom:'1px solid #f3f4f6',
    color:'#374151'
  },
  badge: {
    display:'inline-block', padding:'3px 9px',
    borderRadius:20, fontSize:11, fontWeight:600
  },
  empty:      { textAlign:'center', padding:'32px', color:'#9ca3af', fontSize:13 },
  comingSoon: { textAlign:'center', padding:'32px', color:'#9ca3af', fontSize:13 }
}

function statusBadge(status) {
  const map = {
    unresolved: { background:'#fee2e2', color:'#dc2626' },
    resolved:   { background:'#dcfce7', color:'#16a34a' },
  }
  return { ...S.badge, ...(map[status] || { background:'#f3f4f6', color:'#6b7280' }) }
}

function alertTypeBadge(type) {
  if (type === 'fire')
    return { ...S.badge, background:'#fef3c7', color:'#d97706' }
  return { ...S.badge, background:'#dbeafe', color:'#2563eb' }
}

function fmtTime(iso) {
  return new Date(iso).toLocaleString()
}

export default function UserDashboard({ session, onLogout }) {
  const [alerts,  setAlerts]  = useState([])
  const [sensors, setSensors] = useState([])
  const [count,   setCount]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  // useCallback keeps fetchData stable so ESLint is happy
  // when it is used as a useEffect dependency
  const fetchData = useCallback(async () => {
    try {
      const api = await getAPI()
      const [a, s, c] = await Promise.all([
        api.get('/alerts'),
        api.get('/sensors/live'),
        api.get('/alerts/count'),
      ])
      setAlerts(a.data   || [])
      setSensors(s.data  || [])
      setCount(c.data?.count || 0)
      setError('')
    } catch {
      setError('Could not load data from backend.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 10000)
    return () => clearInterval(id)
  }, [fetchData])

  const micSensors   = sensors.filter(s => s.sensor_type === 'microphone')
  const flameSensors = sensors.filter(s => s.sensor_type === 'flame')

  return (
    <div style={S.page}>
      <Navbar session={session} onLogout={onLogout}
              alertCount={count} role="user" />

      <div style={S.content}>

        {error && (
          <div style={{
            background:'#fee2e2', color:'#dc2626', borderRadius:8,
            padding:'12px 16px', marginBottom:20, fontSize:13
          }}>
            {error}
          </div>
        )}

        <div style={S.grid}>
          <div style={S.card}>
            <div style={S.cardIcon}>🚨</div>
            <div style={S.cardLabel}>Unresolved Alerts</div>
            <div style={{...S.cardVal,
              color: count > 0 ? '#dc2626' : '#16a34a'}}>
              {loading ? '…' : count}
            </div>
          </div>
          <div style={S.card}>
            <div style={S.cardIcon}>🎙️</div>
            <div style={S.cardLabel}>Microphone Sensors</div>
            <div style={{...S.cardVal, color:'#2563eb'}}>
              {loading ? '…' : micSensors.length}
            </div>
          </div>
          <div style={S.card}>
            <div style={S.cardIcon}>🔥</div>
            <div style={S.cardLabel}>Flame Sensors</div>
            <div style={{...S.cardVal, color:'#d97706'}}>
              {loading ? '…' : flameSensors.length}
            </div>
          </div>
          <div style={S.card}>
            <div style={S.cardIcon}>📋</div>
            <div style={S.cardLabel}>Total Alerts</div>
            <div style={S.cardVal}>
              {loading ? '…' : alerts.length}
            </div>
          </div>
        </div>

        <div style={S.section}>
          <div style={S.secTitle}>📡 Live Sensor Status</div>
          {loading ? (
            <div style={S.empty}>Loading sensors…</div>
          ) : sensors.length === 0 ? (
            <div style={S.empty}>
              No sensor data yet. Start the simulator.
            </div>
          ) : (
            <table style={S.table}>
              <thead>
                <tr>
                  {['Device','Type','Zone','Reading','Status','Last Seen']
                    .map(h => <th key={h} style={S.th}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {sensors.map(s => (
                  <tr key={s.id}>
                    <td style={S.td}><strong>{s.device_id}</strong></td>
                    <td style={S.td}>
                      {s.sensor_type === 'microphone' ? '🎙️ Mic' : '🔥 Flame'}
                    </td>
                    <td style={S.td}>{s.zone}</td>
                    <td style={S.td}>
                      {s.sensor_type === 'microphone'
                        ? `${s.sound_db} dB`
                        : `${s.temperature_c}°C`}
                    </td>
                    <td style={S.td}>
                      <span style={s.is_alert
                        ? {...S.badge,background:'#fee2e2',color:'#dc2626'}
                        : {...S.badge,background:'#dcfce7',color:'#16a34a'}
                      }>
                        {s.is_alert ? '🔴 Alert' : '🟢 Normal'}
                      </span>
                    </td>
                    <td style={{...S.td, color:'#9ca3af', fontSize:12}}>
                      {fmtTime(s.recorded_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={S.section}>
          <div style={S.secTitle}>🚨 Alert History</div>
          {loading ? (
            <div style={S.empty}>Loading alerts…</div>
          ) : alerts.length === 0 ? (
            <div style={S.empty}>No alerts recorded yet.</div>
          ) : (
            <table style={S.table}>
              <thead>
                <tr>
                  {['Type','Device','Zone','Reading','Status','Time']
                    .map(h => <th key={h} style={S.th}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {alerts.map(a => (
                  <tr key={a.id}>
                    <td style={S.td}>
                      <span style={alertTypeBadge(a.alert_type)}>
                        {a.alert_type === 'fire' ? '🔥 Fire' : '🪚 Logging'}
                      </span>
                    </td>
                    <td style={S.td}>{a.device_id}</td>
                    <td style={S.td}>{a.zone}</td>
                    <td style={S.td}>
                      {a.sensor_type === 'microphone'
                        ? `${a.sound_db} dB`
                        : `${a.temperature_c}°C`}
                    </td>
                    <td style={S.td}>
                      <span style={statusBadge(a.status)}>
                        {a.status}
                      </span>
                    </td>
                    <td style={{...S.td, fontSize:12, color:'#9ca3af'}}>
                      {fmtTime(a.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div style={{display:'grid',
          gridTemplateColumns:'repeat(auto-fit,minmax(280px,1fr))',gap:16}}>
          <div style={S.section}>
            <div style={S.secTitle}>🗺️ Forest Map</div>
            <div style={S.comingSoon}>Leaflet map — Sprint 5</div>
          </div>
          <div style={S.section}>
            <div style={S.secTitle}>📈 Trend Analysis</div>
            <div style={S.comingSoon}>Charts — Sprint 7</div>
          </div>
        </div>

      </div>
    </div>
  )
}
