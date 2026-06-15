import { useEffect, useState } from 'react'

export default function BackendStatus() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
        const response = await fetch(`${backendUrl}/api/health`)
        setStatus(response.ok ? 'online' : 'offline')
      } catch {
        setStatus('offline')
      }
    }

    checkBackend()
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  if (status === 'online') return null

  return (
    <div style={{
      position: 'fixed',
      top: 10,
      right: 10,
      background: status === 'checking' ? '#fbbf24' : '#ef4444',
      color: 'white',
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '12px',
      zIndex: 1000
    }}>
      🔴 Backend {status === 'checking' ? 'checking...' : 'offline'}
    </div>
  )
}
