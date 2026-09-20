import { useEffect } from 'react'
import { Navigate, Route, Routes, useParams } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { useAuth } from './auth/AuthContext'
import { SchoolContentProvider } from './content/SchoolContentContext'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import AdminUsersPage from './pages/AdminUsersPage'
import AdminClassesPage from './pages/AdminClassesPage'
import AdminRequestsPage from './pages/AdminRequestsPage'
import CommunicationsPage from './pages/CommunicationsPage'
import TeacherRequestsPage from './pages/TeacherRequestsPage'
import MyClassesPage from './pages/MyClassesPage'
import ClassDetailPage from './pages/ClassDetailPage'
import SchoolPickerPage from './pages/SchoolPickerPage'
import PlatformHomePage from './pages/PlatformHomePage'
import StudentRegisterPage from './pages/StudentRegisterPage'
import TeacherRegisterPage from './pages/TeacherRegisterPage'
import ConfirmEmailPage from './pages/ConfirmEmailPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import ProfilePage from './pages/ProfilePage'
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
        <Route path="register/student" element={<StudentRegisterPage />} />
        <Route path="register/teacher" element={<TeacherRegisterPage />} />
        <Route path="confirm-email" element={<ConfirmEmailPage />} />
        <Route path="forgot-password" element={<ForgotPasswordPage />} />
        <Route path="reset-password" element={<ResetPasswordPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="profile" element={<ProfilePage />} />
          <Route path="dashboard/communicate-admin" element={<CommunicationsPage target="admin" />} />
        </Route>

        <Route element={<ProtectedRoute roles={['ADMIN']} />}>
          <Route path="dashboard/admin" element={<DashboardPage />} />
          <Route path="dashboard/admin/users" element={<AdminUsersPage />} />
          <Route path="dashboard/admin/classes" element={<AdminClassesPage />} />
          <Route path="dashboard/admin/requests" element={<AdminRequestsPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['TEACHER']} />}>
          <Route path="dashboard/teacher" element={<DashboardPage />} />
          <Route path="dashboard/teacher/classes" element={<MyClassesPage />} />
          <Route path="dashboard/teacher/classes/:classId" element={<ClassDetailPage />} />
          <Route path="dashboard/teacher/requests" element={<TeacherRequestsPage />} />
        </Route>
        <Route element={<ProtectedRoute roles={['STUDENT']} />}>
          <Route path="dashboard/student" element={<DashboardPage />} />
          <Route path="dashboard/student/classes" element={<MyClassesPage />} />
          <Route path="dashboard/student/classes/:classId" element={<ClassDetailPage />} />
          <Route path="dashboard/student/communicate-teacher" element={<CommunicationsPage target="teacher" />} />
        </Route>

        <Route path="dashboard" element={<DashboardRedirect />} />
        <Route path="*" element={<Navigate to={schoolHomePath()} replace />} />
      </Routes>
    </SchoolContentProvider>
  )
}

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
      <Route path="/" element={<PlatformHomePage />} />
      <Route path="/schools" element={<SchoolPickerPage />} />
      <Route path="/s/:schoolSlug/*" element={<LegacyPathRedirect />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
