import { useState, useEffect } from 'react'
import { resolveBackend } from '../services/api.js'

export default function BackendStatus() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    resolveBackend()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'))
  }, [])

  if (status !== 'error') return null

  return (
    <div style={{
      background:'#fef3c7', borderBottom:'2px solid #d97706',
      padding:'10px 20px', textAlign:'center',
      fontSize:13, color:'#92400e'
    }}>
      ⚠️ No backend reachable. Check Render.com deployment
      or start local backend: <code>cd backend && npm run dev</code>
    </div>
  )
}
