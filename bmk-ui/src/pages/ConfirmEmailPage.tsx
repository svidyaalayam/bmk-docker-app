import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { confirmEmail } from '../api/auth'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { schoolLoginPath } from '../utils/routes'
import { getErrorMessage } from '../utils/errors'

export default function ConfirmEmailPage() {
  const { school, schoolSlug } = useSchoolContent()
  const [params] = useSearchParams()
  const [message, setMessage] = useState('Confirming your email…')
  const [error, setError] = useState('')

  useEffect(() => {
    const uid = params.get('uid') || ''
    const token = params.get('token') || ''
    if (!uid || !token) {
      setError('This confirmation link is incomplete.')
      setMessage('')
      return
    }
    confirmEmail(uid, token)
      .then((data) => {
        setMessage(data.detail)
        setError('')
      })
      .catch((err) => {
        setMessage('')
        setError(getErrorMessage(err, 'Could not confirm email.'))
      })
  }, [params])

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="auth-shell compact">
        <div className="auth-card">
          <p className="brand">{school.school_name || schoolSlug}</p>
          <h1>Email confirmation</h1>
          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
          <p className="auth-footer">
            <Link to={schoolLoginPath()}>Go to Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
