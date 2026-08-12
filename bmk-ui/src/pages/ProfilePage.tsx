import { useEffect, useRef, useState, type FormEvent } from 'react'
import { removeMyAvatar, updateMyProfile, uploadMyAvatar } from '../api/auth'
import { useAuth } from '../auth/AuthContext'
import SiteHeader from '../components/SiteHeader'
import { getErrorMessage } from '../utils/errors'

const MAX_AVATAR_BYTES = 100 * 1024

export default function ProfilePage() {
  const { user, setUserProfile } = useAuth()
  const fileRef = useRef<HTMLInputElement>(null)
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    setFirstName(user.first_name || '')
    setLastName(user.last_name || '')
    setPhone(user.phone_number || '')
  }, [user])

  if (!user) return null

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')
    try {
      const updated = await updateMyProfile({
        first_name: firstName,
        last_name: lastName,
        phone_number: phone || null,
      })
      setUserProfile(updated)
      setMessage('Profile updated.')
    } catch (err) {
      setError(getErrorMessage(err, 'Could not update profile.'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleAvatarChange = async (file: File | null) => {
    if (!file) return
    setError('')
    setMessage('')
    if (file.size > MAX_AVATAR_BYTES) {
      setError(`Avatar must be ${MAX_AVATAR_BYTES / 1024} KB or smaller.`)
      return
    }
    if (!file.type.startsWith('image/')) {
      setError('Please choose an image file (JPEG, PNG, WebP, or GIF).')
      return
    }
    setUploading(true)
    try {
      const updated = await uploadMyAvatar(file)
      setUserProfile(updated)
      setMessage('Avatar updated.')
    } catch (err) {
      setError(getErrorMessage(err, 'Could not upload avatar.'))
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleRemoveAvatar = async () => {
    setUploading(true)
    setError('')
    setMessage('')
    try {
      const updated = await removeMyAvatar()
      setUserProfile(updated)
      setMessage('Avatar removed.')
    } catch (err) {
      setError(getErrorMessage(err, 'Could not remove avatar.'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="dash-shell">
        <header className="dash-header compact">
          <div>
            <p className="brand light">Account</p>
            <h1>My profile</h1>
            <p className="header-sub">
              Update your name and phone. Username and email cannot be changed here.
            </p>
          </div>
        </header>

        <section className="dash-panel">
          <div className="profile-avatar-row">
            <div className="profile-avatar-preview" aria-hidden="true">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt="" />
              ) : (
                <span>
                  {(user.first_name?.[0] || user.username?.[0] || '?').toUpperCase()}
                </span>
              )}
            </div>
            <div className="profile-avatar-actions">
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                hidden
                onChange={(e) => handleAvatarChange(e.target.files?.[0] ?? null)}
              />
              <button
                type="button"
                className="home-btn"
                disabled={uploading}
                onClick={() => fileRef.current?.click()}
              >
                {uploading ? 'Uploading…' : 'Upload avatar'}
              </button>
              {user.avatar_url && (
                <button
                  type="button"
                  className="tab"
                  disabled={uploading}
                  onClick={handleRemoveAvatar}
                >
                  Remove
                </button>
              )}
              <p className="header-sub">JPEG/PNG/WebP/GIF, max {MAX_AVATAR_BYTES / 1024} KB.</p>
            </div>
          </div>

          <form className="admin-form" onSubmit={handleSave}>
            <div className="form-grid">
              <label>
                Username
                <input value={user.username} disabled readOnly />
              </label>
              <label>
                Email
                <input value={user.email || ''} disabled readOnly />
              </label>
              <label>
                First name
                <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              </label>
              <label>
                Last name
                <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
              </label>
              <label>
                Phone
                <input value={phone} onChange={(e) => setPhone(e.target.value)} />
              </label>
            </div>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Saving…' : 'Save profile'}
            </button>
          </form>

          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
        </section>
      </div>
    </div>
  )
}
