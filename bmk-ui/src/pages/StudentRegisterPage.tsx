import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { registerStudent } from '../api/auth'
import SiteHeader from '../components/SiteHeader'
import { useSchoolContent } from '../content/SchoolContentContext'
import { schoolLoginPath } from '../utils/routes'
import { getErrorMessage } from '../utils/errors'

function toApiDate(ddmmyyyy: string): string {
  const m = ddmmyyyy.trim().match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
  if (!m) return ddmmyyyy
  return `${m[3]}-${m[2]}-${m[1]}`
}

export default function StudentRegisterPage() {
  const { school, schoolSlug } = useSchoolContent()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [parentName, setParentName] = useState('')
  const [gender, setGender] = useState<'M' | 'F'>('M')
  const [dob, setDob] = useState('')
  const [phone, setPhone] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (!/^\d{2}\/\d{2}\/\d{4}$/.test(dob.trim())) {
      setError('Date of birth must be dd/mm/yyyy.')
      return
    }
    setSubmitting(true)
    try {
      const data = await registerStudent(
        {
          email: email.trim().toLowerCase(),
          password,
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          parent_name: parentName.trim(),
          gender,
          date_of_birth: toApiDate(dob),
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
          <h1>Student registration</h1>
          <p className="subtitle">
            Please check your details carefully. After you submit, you cannot change them.
          </p>
          <p className="subtitle notice">
            We use date of birth to place students in classes by age, and to send birthday wishes.
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
              <label>
                Parent&apos;s Name
                <input
                  value={parentName}
                  onChange={(e) => setParentName(e.target.value)}
                  required
                />
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
                  Boy
                </label>
                <label className="inline">
                  <input
                    type="radio"
                    name="gender"
                    checked={gender === 'F'}
                    onChange={() => setGender('F')}
                  />
                  Girl
                </label>
              </fieldset>
              <label>
                Date of Birth (dd/mm/yyyy)
                <input
                  placeholder="dd/mm/yyyy"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  required
                />
              </label>
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
