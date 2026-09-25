import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import {
  dashboardPathForRole,
  forgotPasswordPath,
  schoolHomePath,
  studentRegisterPath,
  teacherRegisterPath,
} from '../utils/routes'

export default function LoginPage() {
  const { school, schoolSlug } = useSchoolContent()
  const { user, login, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user && user.school_slug === schoolSlug) {
    return <Navigate to={dashboardPathForRole(user.role)} replace />
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const loggedIn = await login(email.trim(), password, termsAccepted)
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
      setError(detail || 'Login failed. Check your email and password.')
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
          <p className="subtitle">Use the email you registered with.</p>

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Email
              <input
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
            <div className="terms-box">
              <h2>{school.terms_and_conditions.split('\n')[0] || 'Terms & Conditions'}</h2>
              <div className="terms-content">
                {school.terms_and_conditions.split('\n').slice(1).join('\n') ||
                  'Please review the Terms & Conditions.'}
              </div>
            </div>
            <label className="terms-acceptance">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                required
              />
              <span>I have read and agree to the Terms & Conditions.</span>
            </label>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {error && <p className="error">{error}</p>}

          <div className="auth-register-actions">
            <Link to={studentRegisterPath()} className="auth-btn secondary">
              New User Register
            </Link>
            <p className="auth-register-hint">
              Teacher? <Link to={teacherRegisterPath()}>Register as teacher</Link>
            </p>
          </div>

          <div className="auth-links">
            <p>
              <Link to={forgotPasswordPath()}>Forgot password?</Link>
            </p>
            <p>
              <Link to={schoolHomePath()}>Back to homepage</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
