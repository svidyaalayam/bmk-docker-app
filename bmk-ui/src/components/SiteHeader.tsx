import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { useSchoolContent } from '../content/SchoolContentContext'
import HeaderUser from './HeaderUser'
import {
  adminUsersPath,
  dashboardPathForRole,
  schoolHomePath,
  schoolLoginPath,
} from '../utils/routes'
import { platformOrigin } from '../utils/tenant'

function brandMark(schoolName: string): string {
  const words = schoolName.trim().split(/\s+/).filter(Boolean)
  if (words.length >= 2) {
    return `${words[0][0]}${words[1][0]}`.toUpperCase()
  }
  return schoolName.slice(0, 3).toUpperCase() || 'SCH'
}

export default function SiteHeader() {
  const { user, loading } = useAuth()
  const { school, schoolSlug } = useSchoolContent()
  const schoolName = school.school_name || schoolSlug
  const mark = brandMark(schoolName)

  return (
    <header className="site-header">
      <NavLink to={schoolHomePath()} className="site-brand">
        {school.logo_url ? (
          <img
            className="site-brand-logo"
            src={school.logo_url}
            alt={`${schoolName} logo`}
            width={36}
            height={36}
          />
        ) : (
          <span className="site-brand-mark" aria-hidden="true">
            {mark}
          </span>
        )}
        <span className="site-brand-text">{schoolName}</span>
      </NavLink>

      <nav className="site-nav" aria-label="Main">
        <a href={platformOrigin() + '/'} className="nav-link">
          All schools
        </a>
        <NavLink
          to={schoolHomePath()}
          end
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          Home
        </NavLink>

        {!loading && user && user.school_slug === schoolSlug && (
          <NavLink
            to={dashboardPathForRole(user.role)}
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Dashboard
          </NavLink>
        )}

        {!loading && user?.role === 'ADMIN' && user.school_slug === schoolSlug && (
          <NavLink
            to={adminUsersPath()}
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Manage users
          </NavLink>
        )}
      </nav>

      <div className="site-header-right">
        {!loading && !user && (
          <NavLink to={schoolLoginPath()} className="nav-cta">
            Sign in
          </NavLink>
        )}
        {!loading && user && <HeaderUser />}
      </div>
    </header>
  )
}
