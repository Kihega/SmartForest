import { useState } from 'react'
import Login          from './pages/Login.jsx'
import AdminDashboard from './pages/AdminDashboard.jsx'
import UserDashboard  from './pages/UserDashboard.jsx'
import BackendStatus  from './components/BackendStatus.jsx'

export default function App() {
  const [session, setSession] = useState(
    () => JSON.parse(sessionStorage.getItem('sf_session') || 'null')
  )

  function handleLogin(sess) {
    sessionStorage.setItem('sf_session', JSON.stringify(sess))
    setSession(sess)
  }

  function handleLogout() {
    sessionStorage.removeItem('sf_session')
    setSession(null)
  }

  if (!session) {
    return (
      <>
        <BackendStatus />
        <Login onLogin={handleLogin} />
      </>
    )
  }

  if (session.role === 'admin') {
    return <AdminDashboard session={session} onLogout={handleLogout} />
  }

  return <UserDashboard session={session} onLogout={handleLogout} />
}
