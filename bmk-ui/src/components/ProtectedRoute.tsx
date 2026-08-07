import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { useSchoolContent } from '../content/SchoolContentContext'
import type { UserRole } from '../types/auth'
import { dashboardPathForRole, schoolLoginPath } from '../utils/routes'

export function ProtectedRoute({ roles }: { roles?: UserRole[] }) {
  const { schoolSlug } = useSchoolContent()
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="page-center">Checking session…</div>
  }

  if (!user) {
    return <Navigate to={schoolLoginPath()} replace />
  }

  if (user.school_slug && schoolSlug && user.school_slug !== schoolSlug) {
    return <Navigate to={schoolLoginPath()} replace />
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to={dashboardPathForRole(user.role)} replace />
  }

  return <Outlet />
}
