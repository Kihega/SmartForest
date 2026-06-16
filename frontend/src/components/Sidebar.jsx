import { useState } from 'react'

const LANGS = ['English','Swahili','French','Portuguese','Arabic']

export default function Sidebar({ active, onNav, onLogout, mode, onModeChange, lang, onLangChange }) {
  const [modeOpen, setModeOpen] = useState(false)
  const [langOpen,  setLangOpen]  = useState(false)

  const items = [
    { id:'home',    icon:'🏠', label:'Home' },
    { id:'devices', icon:'📡', label:'Devices' },
  ]

  return (
    <aside style={{ ...sb, background: mode==='dark' ? '#1a2a1a' : '#1b5e20' }}>
      {items.map(it => (
        <SBBtn key={it.id} icon={it.icon} label={it.label}
          active={active===it.id} onClick={() => onNav(it.id)} />
      ))}

      {/* change password */}
      <SBBtn icon="🔑" label="Password" onClick={() => onNav('changepassword')} />

      {/* mode toggle */}
      <div style={{ position:'relative' }}>
        <SBBtn icon={mode==='dark' ? '🌙':'☀️'} label="Mode"
          onClick={() => setModeOpen(v => !v)} />
        {modeOpen && (
          <div style={dropdown}>
            {['light','dark'].map(m => (
              <button key={m} style={{ ...ddItem, fontWeight: mode===m ? 700 : 400 }}
                onClick={() => { onModeChange(m); setModeOpen(false) }}>
                {m === 'light' ? '☀️ Light' : '🌙 Dark'}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* translate */}
      <div style={{ position:'relative' }}>
        <SBBtn icon="🌐" label="Language" onClick={() => setLangOpen(v => !v)} />
        {langOpen && (
          <div style={dropdown}>
            {LANGS.map(l => (
              <button key={l} style={{ ...ddItem, fontWeight: lang===l ? 700 : 400 }}
                onClick={() => { onLangChange(l); setLangOpen(false) }}>
                {l}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* logout — pushed to bottom */}
      <div style={{ marginTop:'auto' }}>
        <SBBtn icon="🚪" label="Logout" onClick={onLogout} danger />
      </div>
    </aside>
  )
}

function SBBtn({ icon, label, active, onClick, danger }) {
  const [hover, setHover] = useState(false)
  return (
    <button
      title={label}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display:'flex', flexDirection:'column', alignItems:'center',
        justifyContent:'center', gap:4,
        width:60, padding:'12px 0',
        background: active
          ? 'rgba(255,255,255,0.25)'
          : hover
            ? 'rgba(255,255,255,0.12)'
            : 'transparent',
        border:'none', cursor:'pointer',
        color: danger ? '#ff8a80' : '#fff',
        borderRadius:8, fontSize:20,
        transition:'background .15s',
      }}
    >
      <span>{icon}</span>
      <span style={{ fontSize:9, fontWeight:600, letterSpacing:0.4, opacity:0.85 }}>
        {label}
      </span>
    </button>
  )
}

const sb = {
  width:68, minHeight:'calc(100vh - 56px)',
  display:'flex', flexDirection:'column',
  alignItems:'center', gap:4, paddingTop:12, paddingBottom:12,
  boxShadow:'2px 0 8px rgba(0,0,0,0.15)',
  flexShrink:0,
}
const dropdown = {
  position:'absolute', left:72, top:0,
  background:'#fff', borderRadius:8, minWidth:130,
  boxShadow:'0 4px 20px rgba(0,0,0,0.18)',
  zIndex:200, overflow:'hidden',
}
const ddItem = {
  display:'block', width:'100%', padding:'10px 16px',
  background:'none', border:'none', cursor:'pointer',
  fontSize:13, color:'#1b5e20', textAlign:'left',
}
