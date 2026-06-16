import { useState } from 'react'
import { getAPI } from '../services/api.js'

function strengthLabel(pwd) {
  if (!pwd) return { label:'', color:'#ccc', pct:0 }
  let s = 0
  if (pwd.length >= 8) s++
  if (/[A-Z]/.test(pwd)) s++
  if (/[0-9]/.test(pwd)) s++
  if (/[^A-Za-z0-9]/.test(pwd)) s++
  const map = [
    { label:'Too short', color:'#ef5350', pct:10 },
    { label:'Weak',      color:'#ff7043', pct:30 },
    { label:'Fair',      color:'#ffa726', pct:55 },
    { label:'Good',      color:'#66bb6a', pct:78 },
    { label:'Strong',    color:'#2e7d32', pct:100 },
  ]
  return map[s] || map[0]
}

export default function SignupModal({ onClose, onSuccess }) {
  const [form, setForm] = useState({
    firstName:'', surName:'', email:'',
    phone:'', password:'', confirm:'',
  })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const strength = strengthLabel(form.password)

  function set(k) { return e => setForm(f => ({ ...f, [k]: e.target.value })) }

  async function submit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const api = await getAPI()
      await api.post('/auth/register', {
        firstName: form.firstName,
        surName:   form.surName,
        email:     form.email,
        phone:     form.phone,
        password:  form.password,
      })
      onSuccess()
    } catch (err) {
      setError(err?.response?.data?.error || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={ov} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={card}>
        <div style={header}>
          <span style={{ fontWeight:800, fontSize:18, color:'#1b5e20' }}>Create Account</span>
          <button style={closeBtn} onClick={onClose} aria-label="Close">✕</button>
        </div>

        {error && <div style={errBox} role="alert">{error}</div>}

        <form onSubmit={submit} noValidate style={{ display:'grid', gap:12 }}>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
            <Field label="First Name" id="su-fn" value={form.firstName} onChange={set('firstName')} required />
            <Field label="Surname"    id="su-sn" value={form.surName}   onChange={set('surName')}   required />
          </div>
          <Field label="Email"        id="su-em" type="email"   value={form.email}    onChange={set('email')}    required />
          <Field label="Phone Number" id="su-ph" type="tel"     value={form.phone}    onChange={set('phone')} />
          <Field label="Password"     id="su-pw" type="password" value={form.password} onChange={set('password')} required />

          {/* strength bar */}
          {form.password && (
            <div>
              <div style={{ height:4, background:'#e0e0e0', borderRadius:4, overflow:'hidden' }}>
                <div style={{ width:`${strength.pct}%`, height:'100%', background:strength.color,
                  borderRadius:4, transition:'width .3s, background .3s' }} />
              </div>
              <span style={{ fontSize:11, color:strength.color, fontWeight:600 }}>{strength.label}</span>
            </div>
          )}

          <Field label="Confirm Password" id="su-cp" type="password" value={form.confirm} onChange={set('confirm')} required />

          <button
            type="submit"
            data-testid="signup-submit"
            disabled={loading}
            style={{ ...submitBtn, opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Creating account…' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  )
}

function Field({ label, id, type='text', value, onChange, required }) {
  return (
    <div>
      <label htmlFor={id} style={{ display:'block', fontSize:13, fontWeight:600,
        color:'#2e4a2e', marginBottom:4 }}>
        {label}{required && <span style={{ color:'#c62828' }}> *</span>}
      </label>
      <input
        id={id}
        data-testid={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        style={{ width:'100%', padding:'9px 12px', fontSize:13,
          border:'1.5px solid #c8e6c9', borderRadius:7, outline:'none',
          background:'#f9fef9', color:'#1b5e20' }}
      />
    </div>
  )
}

const ov = {
  position:'fixed', inset:0, background:'rgba(0,0,0,0.55)',
  display:'flex', alignItems:'center', justifyContent:'center',
  zIndex:1000, padding:16,
}
const card = {
  background:'#fff', borderRadius:14, padding:'28px 32px',
  width:'100%', maxWidth:480,
  boxShadow:'0 16px 48px rgba(0,60,0,0.18)',
  maxHeight:'90vh', overflowY:'auto',
}
const header = {
  display:'flex', justifyContent:'space-between',
  alignItems:'center', marginBottom:20,
}
const closeBtn = {
  background:'none', border:'none', fontSize:18,
  cursor:'pointer', color:'#555', lineHeight:1,
}
const errBox = {
  background:'#ffebee', color:'#c62828', borderRadius:7,
  padding:'9px 12px', fontSize:13, marginBottom:12,
}
const submitBtn = {
  width:'100%', padding:12, fontSize:14,
  fontWeight:700, background:'#2e7d32', color:'#fff',
  border:'none', borderRadius:8, cursor:'pointer', marginTop:4,
}
