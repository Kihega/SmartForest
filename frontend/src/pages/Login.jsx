import { useState } from 'react'
import { getAPI }   from '../services/api.js'

const S = {
  wrap: {
    minHeight:'100vh', display:'flex',
    alignItems:'center', justifyContent:'center',
    background:'linear-gradient(135deg,#14532d 0%,#16a34a 100%)'
  },
  card: {
    background:'#fff', borderRadius:12, padding:'40px 36px',
    width:'100%', maxWidth:400,
    boxShadow:'0 8px 32px rgba(0,0,0,0.18)'
  },
  logo: {
    display:'flex', alignItems:'center', gap:10,
    marginBottom:28
  },
  icon: {
    width:44, height:44, borderRadius:10,
    background:'#16a34a', display:'flex',
    alignItems:'center', justifyContent:'center',
    fontSize:22
  },
  title:   { fontSize:20, fontWeight:700, color:'#111827' },
  sub:     { fontSize:13, color:'#6b7280', marginTop:2 },
  label:   { display:'block', fontSize:13, fontWeight:600,
             color:'#374151', marginBottom:6 },
  input:   {
    width:'100%', padding:'10px 12px', fontSize:14,
    border:'1.5px solid #e5e7eb', borderRadius:8,
    outline:'none', marginBottom:16
  },
  btn: {
    width:'100%', padding:'11px', fontSize:15,
    fontWeight:600, background:'#16a34a', color:'#fff',
    borderRadius:8, marginTop:4
  },
  err: {
    background:'#fee2e2', color:'#dc2626', borderRadius:8,
    padding:'10px 12px', fontSize:13, marginBottom:14
  },
  role: {
    marginTop:20, padding:'12px 14px',
    background:'#f0fdf4', borderRadius:8,
    fontSize:12, color:'#166534'
  }
}

export default function Login({ onLogin }) {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const api = await getAPI()
      const res = await api.post('/auth/login', { email, password })
      onLogin(res.data)
    } catch (err) {
      setError(
        err?.response?.data?.error ||
        'Login failed. Check your credentials.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={S.wrap}>
      <div style={S.card}>
        <div style={S.logo}>
          <div style={S.icon}>🌿</div>
          <div>
            <div style={S.title}>SmartForest</div>
            <div style={S.sub}>Illegal Logging Detection System</div>
          </div>
        </div>

        {error && <div style={S.err}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <label style={S.label}>Email address</label>
          <input
            style={S.input}
            type="email"
            placeholder="ranger@smartforest.tz"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
          <label style={S.label}>Password</label>
          <input
            style={S.input}
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <button style={S.btn} type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={S.role}>
          <strong>Admin</strong> — full system access (devices, users, settings)<br/>
          <strong>User</strong> — view alerts and trends for your registered devices
        </div>
      </div>
    </div>
  )
}
