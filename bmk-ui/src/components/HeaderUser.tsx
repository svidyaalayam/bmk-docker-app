import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { getDisplayName, getInitials } from '../utils/userDisplay'
import { schoolHomePath } from '../utils/routes'

export default function HeaderUser() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onClickOutside = (event: MouseEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  if (!user) return null

  const name = getDisplayName(user)
  const initials = getInitials(user)

  const handleLogout = () => {
    logout()
    setOpen(false)
    navigate(schoolHomePath(), { replace: true })
  }

  return (
    <div className="header-user" ref={menuRef}>
      <button
        type="button"
        className="header-user-trigger"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-haspopup="menu"
      >
        <span className="header-user-name">{name}</span>
        <span className="user-avatar" aria-hidden="true">
          {initials}
        </span>
      </button>

      {open && (
        <div className="header-user-menu" role="menu">
          <div className="header-user-meta">
            <p className="header-user-meta-name">{name}</p>
            <p className="header-user-meta-role">{user.role}</p>
            {user.email && <p className="header-user-meta-email">{user.email}</p>}
          </div>
          <button type="button" role="menuitem" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      )}
    </div>
  )
}
