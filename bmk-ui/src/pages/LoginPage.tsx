import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { dashboardPathForRole, schoolHomePath } from '../utils/routes'

const DEMO_ACCOUNTS: Record<string, { admin: string; teacher: string; student: string }> = {
  balamukundam: {
    admin: 'bmk_admin',
    teacher: 'bmk_teacher',
    student: 'bmk_student',
  },
  balavikas: {
    admin: 'bv_admin',
    teacher: 'bv_teacher',
    student: 'bv_student',
  },
}

export default function LoginPage() {
  const { school, schoolSlug } = useSchoolContent()
  const { user, login, loading } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const demos = DEMO_ACCOUNTS[schoolSlug]

  if (!loading && user && user.school_slug === schoolSlug) {
    return <Navigate to={dashboardPathForRole(user.role)} replace />
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const loggedIn = await login(username.trim(), password, schoolSlug)
      navigate(dashboardPathForRole(loggedIn.role), { replace: true })
    } catch (err: unknown) {
      const detail =
        typeof err === 'object' &&
        err !== null &&
        'response' in err &&
        typeof (err as { response?: { data?: { detail?: unknown } } }).response?.data?.detail ===
          'string'
          ? (err as { response: { data: { detail: string } } }).response.data.detail
          : null
      setError(detail || 'Login failed. Check your username, password, and school.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-shell">
      <SiteHeader />

      <div className="auth-shell compact">
        <div className="auth-card">
          <p className="brand">{school.school_name || schoolSlug}</p>
          <h1>Sign in</h1>
          <p className="subtitle">JWT-secured access for students, teachers, and admins.</p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Username
              <input
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {error && <p className="error">{error}</p>}

          <div className="demo-hint">
            <p>
              Demo accounts (password: <code>Demo@12345</code>)
            </p>
            {demos ? (
              <ul>
                <li>{demos.admin} — ADMIN</li>
                <li>{demos.teacher} — TEACHER</li>
                <li>{demos.student} — STUDENT</li>
              </ul>
            ) : (
              <p>Use accounts created for this school.</p>
            )}
            <p>
              <Link to={schoolHomePath()}>Back to homepage</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
