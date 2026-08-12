import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { getDisplayName, getInitials } from '../utils/userDisplay'
import { profilePath, schoolHomePath } from '../utils/routes'

function avatarSrc(url?: string | null): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url, window.location.origin)
    // Prefer same-origin path so Vite/Nginx proxies work.
    if (parsed.origin === window.location.origin || parsed.pathname.startsWith('/media/')) {
      return parsed.pathname + parsed.search
    }
    return url
  } catch {
    return url
  }
}

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
  const photo = avatarSrc(user.avatar_url)

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
          {photo ? <img src={photo} alt="" /> : initials}
        </span>
      </button>

      {open && (
        <div className="header-user-menu" role="menu">
          <div className="header-user-meta">
            <p className="header-user-meta-name">{name}</p>
            <p className="header-user-meta-role">{user.role}</p>
            {user.email && <p className="header-user-meta-email">{user.email}</p>}
          </div>
          <Link
            to={profilePath()}
            role="menuitem"
            className="header-user-link"
            onClick={() => setOpen(false)}
          >
            Edit profile
          </Link>
          <button type="button" role="menuitem" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      )}
    </div>
  )
}
