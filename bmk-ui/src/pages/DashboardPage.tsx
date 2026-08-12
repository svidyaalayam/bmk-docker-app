import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchDashboard } from '../api/auth'
import { useAuth } from '../auth/AuthContext'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import type { DashboardPayload } from '../types/auth'
import { adminClassesPath, adminUsersPath, myClassesPath } from '../utils/routes'

const ROLE_LABELS = {
  ADMIN: 'Administrator',
  TEACHER: 'Teacher',
  STUDENT: 'Student',
} as const

export default function DashboardPage() {
  const { school, schoolSlug } = useSchoolContent()
  const { user } = useAuth()
  const [payload, setPayload] = useState<DashboardPayload | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    fetchDashboard(user.role)
      .then(setPayload)
      .catch(() => setError('Could not load role dashboard from the API.'))
  }, [user])

  if (!user) return null

  return (
    <div className="page-shell">
      <SiteHeader />

      <div className="dash-shell">
        <header className="dash-header compact">
          <div>
            <p className="brand light">{school.school_name || schoolSlug}</p>
            <h1>{ROLE_LABELS[user.role]} Dashboard</h1>
          </div>
        </header>

        <section className="dash-panel">
          <p className="welcome">
            Signed in as <strong>{user.username}</strong> ({user.email || 'no email'})
          </p>
          <p className="role-badge">{user.role}</p>

          {error && <p className="error">{error}</p>}

          {payload && (
            <>
              <p>{payload.message}</p>
              <h2>Capabilities</h2>
              <ul>
                {payload.capabilities.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          )}

          {user.role === 'ADMIN' && (
            <p className="admin-cta">
              {typeof payload?.pending_activations === 'number' &&
                payload.pending_activations > 0 && (
                  <>
                    {payload.pending_activations} user
                    {payload.pending_activations === 1 ? '' : 's'} waiting for activation.{' '}
                  </>
                )}
              <Link to={adminUsersPath()}>Open user management →</Link>
              {' · '}
              <Link to={adminClassesPath()}>Open class management →</Link>
            </p>
          )}

          {(user.role === 'TEACHER' || user.role === 'STUDENT') && (
            <p className="admin-cta">
              <Link to={myClassesPath(user.role)}>Open my classes →</Link>
            </p>
          )}
        </section>
      </div>
    </div>
  )
}
