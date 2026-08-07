import { useEffect } from 'react'
import { Navigate, Route, Routes, useParams } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { useAuth } from './auth/AuthContext'
import { SchoolContentProvider } from './content/SchoolContentContext'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import AdminUsersPage from './pages/AdminUsersPage'
import SchoolPickerPage from './pages/SchoolPickerPage'
import { dashboardPathForRole, schoolHomePath, schoolLoginPath } from './utils/routes'
import { getSchoolSlugFromHost, schoolSiteUrl } from './utils/tenant'
import './App.css'

function DashboardRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-center">Loading…</div>
  if (!user) return <Navigate to={schoolLoginPath()} replace />
  return <Navigate to={dashboardPathForRole(user.role)} replace />
}

function SchoolRoutes({ schoolSlug }: { schoolSlug: string }) {
  return (
    <SchoolContentProvider schoolSlug={schoolSlug}>
      <Routes>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />

        <Route element={<ProtectedRoute roles={['ADMIN']} />}>
          <Route path="dashboard/admin" element={<DashboardPage />} />
          <Route path="dashboard/admin/users" element={<AdminUsersPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['TEACHER']} />}>
          <Route path="dashboard/teacher" element={<DashboardPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['STUDENT']} />}>
          <Route path="dashboard/student" element={<DashboardPage />} />
        </Route>

        <Route path="dashboard" element={<DashboardRedirect />} />
        <Route path="*" element={<Navigate to={schoolHomePath()} replace />} />
      </Routes>
    </SchoolContentProvider>
  )
}

/** Old path URLs like /s/balavikas → http://balavikas.localhost:5173/ */
function LegacyPathRedirect() {
  const { schoolSlug = '' } = useParams()
  useEffect(() => {
    if (schoolSlug) {
      window.location.replace(schoolSiteUrl(schoolSlug, '/'))
    }
  }, [schoolSlug])
  return <div className="page-center">Opening {schoolSlug}…</div>
}

export default function App() {
  const schoolSlug = getSchoolSlugFromHost()

  if (schoolSlug) {
    return <SchoolRoutes schoolSlug={schoolSlug} />
  }

  return (
    <Routes>
      <Route path="/" element={<SchoolPickerPage />} />
      <Route path="/s/:schoolSlug/*" element={<LegacyPathRedirect />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
