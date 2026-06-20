/* Sidebar — lucide-style SVG icons, no emoji.
   Items from handwritten notes:
     Home | Manage Devices | Manage Users | System Performance | Settings
   Bottom: Change Password | Mode toggle | Language | Logout
*/
import { useState } from 'react'

const LANGS = ['English','Swahili','French','Portuguese','Arabic']

/* ── All inline SVG icons ─────────────────────────────────────────────── */
const ICONS = {
  home:        ['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z', 'M9 22V12h6v10'],
  devices:     ['M8 6h13', 'M8 12h13', 'M8 18h13', 'M3 6h.01', 'M3 12h.01', 'M3 18h.01'],
  users:       ['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2', 'M9 7a4 4 0 100 8 4 4 0 000-8z',
                'M23 21v-2a4 4 0 00-3-3.87', 'M16 3.13a4 4 0 010 7.75'],
  performance: ['M18 20V10', 'M12 20V4', 'M6 20v-6'],
  settings:    ['M12 20a8 8 0 100-16 8 8 0 000 16z',
                'M12 14a2 2 0 100-4 2 2 0 000 4z'],
  password:    ['M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4'],
  sun:         ['M12 1v2','M12 21v2','M4.22 4.22l1.42 1.42','M18.36 18.36l1.42 1.42',
                'M1 12h2','M21 12h2','M4.22 19.78l1.42-1.42','M18.36 5.64l1.42-1.42',
                'M12 17a5 5 0 100-10 5 5 0 000 10z'],
  moon:        ['M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z'],
  globe:       ['M12 2a10 10 0 100 20A10 10 0 0012 2z',
                'M2 12h20','M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20'],
  logout:      ['M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4',
                'M16 17l5-5-5-5','M21 12H9'],
  rangers:     ['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2','M9 7a4 4 0 100 8 4 4 0 000-8z',
                'M19 8v6','M22 11h-6'],
  district:    ['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z','M9 22V12h6v10'],
}

function SvgIcon({ name, size=20 }) {
  const d = ICONS[name] || ICONS.home
  if (name === 'devices') {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        {d.map((p, i) => <path key={i} d={p}/>)}
      </svg>
    )
  }
  if (Array.isArray(d)) {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
        stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        {d.map((p, i) => <path key={i} d={p}/>)}
      </svg>
    )
  }
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d={d}/>
    </svg>
  )
}

/* ── Sidebar ─────────────────────────────────────────────────────────────
   `items` can be overridden via props for role-specific navigation
   (e.g. Forest Officer gets a "Rangers" item instead of "Users").       ── */
export default function Sidebar({ active, onNav, onLogout, mode, onModeChange, lang, onLangChange, items: itemsProp }) {
  const [modeOpen, setModeOpen] = useState(false)
  const [langOpen, setLangOpen] = useState(false)

  const items = itemsProp || [
    { id:'home',        iconName:'home',        label:'Home'        },
    { id:'devices',     iconName:'devices',     label:'Devices'     },
    { id:'users',       iconName:'users',       label:'Users'       },
    { id:'performance', iconName:'performance', label:'Performance' },
    { id:'settings',    iconName:'settings',    label:'Settings'    },
  ]

  return (
    <aside style={{ ...sb, background: mode==='dark' ? '#1a2a1a' : '#1b5e20' }}>
      {items.map(it => (
        <SBBtn key={it.id} icon={<SvgIcon name={it.iconName} />} label={it.label}
          active={active===it.id} onClick={() => onNav(it.id)} />
      ))}

      {/* Divider */}
      <div style={{ width:40, height:1, background:'rgba(255,255,255,0.2)', margin:'6px 0' }} />

      {/* Change password */}
      <SBBtn icon={<SvgIcon name="password" />} label="Password" onClick={() => onNav('changepassword')} />

      {/* Mode toggle */}
      <div style={{ position:'relative' }}>
        <SBBtn icon={<SvgIcon name={mode==='dark' ? 'moon' : 'sun'} />} label="Mode"
          onClick={() => setModeOpen(v => !v)} />
        {modeOpen && (
          <div style={dropdown}>
            {['light','dark'].map(m => (
              <button key={m} style={{ ...ddItem, fontWeight: mode===m ? 700 : 400 }}
                onClick={() => { onModeChange(m); setModeOpen(false) }}>
                {m === 'light' ? 'Light' : 'Dark'}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Language */}
      <div style={{ position:'relative' }}>
        <SBBtn icon={<SvgIcon name="globe" />} label="Language" onClick={() => setLangOpen(v => !v)} />
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

      {/* Logout — pushed to bottom */}
      <div style={{ marginTop:'auto' }}>
        <SBBtn icon={<SvgIcon name="logout" />} label="Logout" onClick={onLogout} danger />
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
        borderRadius:8,
        transition:'background .15s',
      }}
    >
      {icon}
      <span style={{ fontSize:9, fontWeight:600, letterSpacing:0.4, opacity:0.85 }}>
        {label}
      </span>
    </button>
  )
}

const sb = {
  width:68, minHeight:'calc(100vh - 54px)',
  display:'flex', flexDirection:'column',
  alignItems:'center', gap:2, paddingTop:12, paddingBottom:12,
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
