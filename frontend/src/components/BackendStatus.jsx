
import { useEffect, useState } from 'react'
import { resolveBackend, resetBackend, BACKEND_CANDIDATES } from '../config/backends.js'

export default function BackendStatus() {
  const [status,  setStatus]  = useState('checking')   // 'checking' | 'online' | 'offline'
  const [backendUrl, setUrl]  = useState('')

  async function check() {
    setStatus('checking')
    try {
      const url = await resolveBackend()
      setUrl(url)
      setStatus('online')
    } catch {
      setStatus('offline')
    }
  }

  useEffect(() => {
    check()
    const t = setInterval(check, 30_000)
    return () => clearInterval(t)
  }, [])

  if (status === 'online') return null

  return (
    <div style={status === 'checking' ? styles.checking : styles.offline}>
      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
        <span>{status === 'checking' ? '🟡' : '🔴'}</span>
        <div>
          <div style={{ fontWeight:700, fontSize:13 }}>
            Backend {status === 'checking' ? 'connecting…' : 'offline'}
          </div>
          {status === 'offline' && (
            <div style={{ fontSize:11, opacity:0.85, marginTop:2 }}>
              Tried: {BACKEND_CANDIDATES.join(', ')}
            </div>
          )}
        </div>
        {status === 'offline' && (
          <button onClick={() => { resetBackend(); check() }} style={styles.retryBtn}>
            Retry
          </button>
        )}
      </div>
    </div>
  )
}

const base = {
  position:'fixed', top:12, right:12,
  padding:'10px 14px', borderRadius:8,
  color:'#fff', zIndex:9999,
  boxShadow:'0 2px 12px rgba(0,0,0,0.25)',
  maxWidth:340, fontFamily:'system-ui,sans-serif',
}
const styles = {
  checking: { ...base, background:'#d97706' },
  offline:  { ...base, background:'#dc2626' },
  retryBtn: {
    background:'rgba(255,255,255,0.25)', border:'1px solid rgba(255,255,255,0.5)',
    color:'#fff', borderRadius:6, padding:'4px 10px',
    fontSize:12, cursor:'pointer', marginLeft:4,
  },
}
