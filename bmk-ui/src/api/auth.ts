import { api } from './client'
import type { DashboardPayload, LoginResponse, User } from '../types/auth'

export async function login(
  username: string,
  password: string,
  schoolSlug?: string,
): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>(
    '/api/auth/login/',
    { username, password },
    schoolSlug ? { params: { school: schoolSlug } } : undefined,
  )
  return data
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me/')
  return data
}

export async function fetchDashboard(role: User['role']): Promise<DashboardPayload> {
  const path =
    role === 'ADMIN'
      ? '/api/auth/dashboard/admin/'
      : role === 'TEACHER'
        ? '/api/auth/dashboard/teacher/'
        : '/api/auth/dashboard/student/'
  const { data } = await api.get<DashboardPayload>(path)
  return data
}
