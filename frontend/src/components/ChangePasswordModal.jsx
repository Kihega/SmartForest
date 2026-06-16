import { useState } from 'react'
import { getAPI } from '../services/api.js'

export default function ChangePasswordModal({ session, onClose }) {
  const [current,  setCurrent]  = useState('')
  const [newPwd,   setNewPwd]   = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')
  const [loading,  setLoading]  = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError(''); setSuccess('')
    if (newPwd !== confirm) { setError('New passwords do not match.'); return }
    if (newPwd.length < 8)  { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      const api = await getAPI()
      await api.post('/auth/change-password',
        { currentPassword: current, newPassword: newPwd },
        { headers: { Authorization: `Bearer ${session.token}` } }
      )
      setSuccess('Password changed successfully!')
      setTimeout(onClose, 1500)
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to change password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={ov} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={card}>
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:20 }}>
          <span style={{ fontWeight:800, fontSize:17, color:'#1b5e20' }}>Change Password</span>
          <button style={closeBtn} onClick={onClose}>✕</button>
        </div>
        {error   && <div style={errBox}>{error}</div>}
        {success && <div style={okBox}>{success}</div>}
        <form onSubmit={submit} noValidate style={{ display:'grid', gap:14 }}>
          {[
            ['Current password', current, setCurrent, 'cp-cur'],
            ['New password',     newPwd,  setNewPwd,  'cp-new'],
            ['Confirm new',      confirm, setConfirm, 'cp-cnf'],
          ].map(([lbl, val, fn, id]) => (
            <div key={id}>
              <label htmlFor={id} style={lStyle}>{lbl}</label>
              <input id={id} data-testid={id} type="password" value={val}
                onChange={e => fn(e.target.value)} required
                style={iStyle} autoComplete="new-password" />
            </div>
          ))}
          <button type="submit" disabled={loading}
            style={{ ...subBtn, opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
const ov      = { position:'fixed', inset:0, background:'rgba(0,0,0,0.6)',
  display:'flex', alignItems:'center', justifyContent:'center', zIndex:1000 }
const card    = { background:'#fff', borderRadius:12, padding:'28px 32px',
  width:'100%', maxWidth:380, boxShadow:'0 12px 40px rgba(0,0,0,0.2)' }
const closeBtn= { background:'none', border:'none', fontSize:18, cursor:'pointer', color:'#555' }
const errBox  = { background:'#ffebee', color:'#c62828', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:8 }
const okBox   = { background:'#e8f5e9', color:'#1b5e20', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:8 }
const lStyle  = { display:'block', fontSize:13, fontWeight:600, color:'#2e4a2e', marginBottom:4 }
const iStyle  = { width:'100%', padding:'9px 12px', fontSize:13,
  border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none' }
const subBtn  = { width:'100%', padding:11, fontSize:14, fontWeight:700,
  background:'#2e7d32', color:'#fff', border:'none', borderRadius:8, cursor:'pointer' }
