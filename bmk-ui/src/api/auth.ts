import { api } from './client'
import type { DashboardPayload, LoginResponse, User } from '../types/auth'

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const body =
    username.includes('@')
      ? { email: username.trim().toLowerCase(), password }
      : { username: username.trim(), password }
  const { data } = await api.post<LoginResponse>('/api/auth/login/', body)
  return data
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me/')
  return data
}

export async function updateMyProfile(payload: {
  first_name?: string
  last_name?: string
  phone_number?: string | null
}): Promise<User> {
  const { data } = await api.patch<User>('/api/auth/me/', payload)
  return data
}

export async function uploadMyAvatar(file: File): Promise<User> {
  const form = new FormData()
  form.append('avatar', file)
  const { data } = await api.post<User>('/api/auth/me/avatar/', form)
  return data
}

export async function removeMyAvatar(): Promise<User> {
  const { data } = await api.delete<User>('/api/auth/me/avatar/')
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

export interface StudentRegisterPayload {
  email: string
  password: string
  first_name: string
  last_name: string
  parent_name: string
  gender: 'M' | 'F'
  date_of_birth: string
  phone: string
}

export interface TeacherRegisterPayload {
  email: string
  password: string
  first_name: string
  last_name: string
  gender: 'M' | 'F'
  phone: string
}

export async function registerStudent(
  payload: StudentRegisterPayload,
): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>(
    '/api/auth/register/student/',
    payload,
  )
  return data
}

export async function registerTeacher(
  payload: TeacherRegisterPayload,
): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>(
    '/api/auth/register/teacher/',
    payload,
  )
  return data
}

export async function confirmEmail(uid: string, token: string): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>('/api/auth/confirm-email/', { uid, token })
  return data
}

export async function requestPasswordReset(
  email: string,
): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>(
    '/api/auth/password-reset/',
    { email },
  )
  return data
}

export async function confirmPasswordReset(
  uid: string,
  token: string,
  password: string,
): Promise<{ detail: string }> {
  const { data } = await api.post<{ detail: string }>('/api/auth/password-reset/confirm/', {
    uid,
    token,
    password,
  })
  return data
}

export async function listPendingUsers(): Promise<User[]> {
  const { data } = await api.get<User[]>('/api/auth/pending-users/')
  return data
}

export async function activateUser(userId: number): Promise<User> {
  const { data } = await api.post<User>(`/api/auth/users/${userId}/activate/`)
  return data
}

export async function deactivateUser(userId: number): Promise<User> {
  const { data } = await api.post<User>(`/api/auth/users/${userId}/deactivate/`)
  return data
}
