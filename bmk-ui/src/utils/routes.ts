import type { UserRole } from '../types/auth'

export function schoolHomePath(_schoolSlug?: string): string {
  return '/'
}

export function schoolLoginPath(_schoolSlug?: string): string {
  return '/login'
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
