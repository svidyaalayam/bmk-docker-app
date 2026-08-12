import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { confirmPasswordReset } from '../api/auth'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { schoolLoginPath } from '../utils/routes'
import { getErrorMessage } from '../utils/errors'

export default function ResetPasswordPage() {
  const { school, schoolSlug } = useSchoolContent()
  const [params] = useSearchParams()
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const uid = params.get('uid') || ''
  const token = params.get('token') || ''

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')
    try {
      const data = await confirmPasswordReset(uid, token, password)
      setMessage(data.detail)
    } catch (err) {
      setError(getErrorMessage(err, 'Could not reset password.'))
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
          <h1>Reset password</h1>
          {!uid || !token ? (
            <p className="error">This reset link is incomplete.</p>
          ) : message ? (
            <p className="success">{message}</p>
          ) : (
            <form onSubmit={handleSubmit} className="auth-form">
              <label>
                New password
                <input
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                />
              </label>
              <button type="submit" disabled={submitting}>
                {submitting ? 'Saving…' : 'Save new password'}
              </button>
            </form>
          )}
          {error && <p className="error">{error}</p>}
          <p className="auth-footer">
            <Link to={schoolLoginPath()}>Back to Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
