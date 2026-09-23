import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { useSchoolContent } from '../content/SchoolContentContext'
import HeaderUser from './HeaderUser'
import { scriptClassForLanguage } from '../types/content'
import {
  dashboardPathForRole,
  schoolHomePath,
  schoolLoginPath,
} from '../utils/routes'

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
  const brandLanguage = school.secondary_language
  const brandScriptClass = scriptClassForLanguage(brandLanguage)
  const mark = brandMark(schoolName)
  // Match ProtectedRoute: allow users with no school_slug yet, or matching school
  const onSchool =
    !loading &&
    !!user &&
    !!schoolSlug &&
    (!user.school_slug || user.school_slug === schoolSlug)

  return (
    <header className="site-header">
      <NavLink to={schoolHomePath()} className="site-brand">
        {school.logo_url ? (
          <img
            className="site-brand-logo"
            src={school.logo_url}
            alt={`${schoolName} logo`}
            width={100}
            height={100}
          />
        ) : (
          <span className="site-brand-mark" aria-hidden="true">
            {mark}
          </span>
        )}
        <span className="site-brand-copy">
          <span className={`site-brand-main-text ${brandScriptClass}`} lang={brandLanguage || 'en'}>
            {schoolName}
          </span>
          {school.tagline && (
            <span className={`site-brand-sub-text ${brandScriptClass}`} lang={brandLanguage || 'en'}>
              {school.tagline}
            </span>
          )}
        </span>
      </NavLink>

      <nav className="site-nav" aria-label="Main">
        <NavLink
          to={schoolHomePath()}
          end
          className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
        >
          Home
        </NavLink>

        {onSchool && user && (
          <NavLink
            to={dashboardPathForRole(user.role)}
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Dashboard
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
