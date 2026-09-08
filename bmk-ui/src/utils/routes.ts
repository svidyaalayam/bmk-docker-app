import type { UserRole } from '../types/auth'

export function schoolHomePath(_schoolSlug?: string): string {
  return '/'
}

export function schoolLoginPath(_schoolSlug?: string): string {
  return '/login'
}

export function studentRegisterPath(): string {
  return '/register/student'
}

export function teacherRegisterPath(): string {
  return '/register/teacher'
}

export function forgotPasswordPath(): string {
  return '/forgot-password'
}

export function confirmEmailPath(): string {
  return '/confirm-email'
}

export function resetPasswordPath(): string {
  return '/reset-password'
}

export function dashboardPathForRole(role: UserRole, _schoolSlug?: string | null): string {
  switch (role) {
    case 'ADMIN':
      return '/dashboard/admin'
    case 'TEACHER':
      return '/dashboard/teacher'
    case 'STUDENT':
      return '/dashboard/student'
    default:
      return '/'
  }
}

export function adminUsersPath(): string {
  return '/dashboard/admin/users'
}

export function adminClassesPath(): string {
  return '/dashboard/admin/classes'
}

export function adminRequestsPath(): string { return '/dashboard/admin/requests' }
export function adminCommunicationPath(): string { return '/dashboard/communicate-admin' }
export function teacherCommunicationPath(): string { return '/dashboard/student/communicate-teacher' }
export function teacherRequestsPath(): string { return '/dashboard/teacher/requests' }

export function myClassesPath(role: UserRole): string {
  if (role === 'TEACHER') return '/dashboard/teacher/classes'
  if (role === 'STUDENT') return '/dashboard/student/classes'
  return dashboardPathForRole(role)
}

export function classDetailPath(role: UserRole, classId: number): string {
  if (role === 'TEACHER') return `/dashboard/teacher/classes/${classId}`
  if (role === 'STUDENT') return `/dashboard/student/classes/${classId}`
  return `/dashboard/admin/classes`
}

export function profilePath(): string {
  return '/profile'
}
