import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { requestPasswordReset } from '../api/auth'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { schoolLoginPath } from '../utils/routes'
import { getErrorMessage } from '../utils/errors'

export default function ForgotPasswordPage() {
  const { school, schoolSlug } = useSchoolContent()
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')
    try {
      const data = await requestPasswordReset(email.trim().toLowerCase())
      setMessage(data.detail)
    } catch (err) {
      setError(getErrorMessage(err, 'Could not send reset email.'))
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
          <h1>Forgot password</h1>
          <p className="subtitle">Enter your email and we will send a reset link.</p>
          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Sending…' : 'Send reset link'}
            </button>
          </form>
          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
          <p className="auth-footer">
            <Link to={schoolLoginPath()}>Back to Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
