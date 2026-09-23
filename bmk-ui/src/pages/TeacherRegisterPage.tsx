import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { registerTeacher } from '../api/auth'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { schoolLoginPath } from '../utils/routes'
import { getErrorMessage } from '../utils/errors'

export default function TeacherRegisterPage() {
  const { school, schoolSlug } = useSchoolContent()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [gender, setGender] = useState<'M' | 'F'>('M')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setSubmitting(true)
    try {
      const data = await registerTeacher(
        {
          email: email.trim().toLowerCase(),
          password,
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          gender,
          phone: phone.trim(),
        },
      )
      setMessage(data.detail)
    } catch (err) {
      setError(getErrorMessage(err, 'Registration failed.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="auth-shell">
        <div className="auth-card wide">
          <p className="brand">{school.school_name || schoolSlug}</p>
          <h1>Teacher registration</h1>
          <p className="subtitle">
            Please check your details carefully. After you submit, you cannot change them.
          </p>

          {message ? (
            <p className="success">{message}</p>
          ) : (
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
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                />
              </label>
              <label>
                Name
                <input
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </label>
              <label>
                Surname
                <input value={lastName} onChange={(e) => setLastName(e.target.value)} required />
              </label>
              <fieldset className="radio-row">
                <legend>Gender</legend>
                <label className="inline">
                  <input
                    type="radio"
                    name="gender"
                    checked={gender === 'M'}
                    onChange={() => setGender('M')}
                  />
                  Male
                </label>
                <label className="inline">
                  <input
                    type="radio"
                    name="gender"
                    checked={gender === 'F'}
                    onChange={() => setGender('F')}
                  />
                  Female
                </label>
              </fieldset>
              <label>
                Contact Number
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </label>
              <button type="submit" disabled={submitting}>
                {submitting ? 'Submitting…' : 'Register'}
              </button>
            </form>
          )}

          {error && <p className="error">{error}</p>}

          <p className="auth-footer">
            Have an account? <Link to={schoolLoginPath()}>Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
