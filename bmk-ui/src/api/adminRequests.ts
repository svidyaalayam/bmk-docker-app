import { api } from './client'
import type { User } from '../types/auth'

export type AdminRequest = { id: number; user: User; kind: 'REQUEST' | 'FEEDBACK'; subject: string; message: string; reply: string; replied_by_name: string | null; resolved: boolean; resolved_at: string | null; created_at: string; updated_at: string }

export async function sendAdminRequest(payload: { kind: 'REQUEST' | 'FEEDBACK'; subject: string; message: string }) {
  const { data } = await api.post<AdminRequest>('/api/my-admin-requests/', payload)
  return data
}
export async function listMyAdminRequests() {
  const { data } = await api.get<AdminRequest[]>('/api/my-admin-requests/')
  return data
}
export async function listAdminRequests(params: { page: number; status?: string; kind?: string }) {
  const { data } = await api.get<{ count: number; page: number; page_size: number; results: AdminRequest[] }>('/api/admin-requests/', { params })
  return data
}
export async function updateAdminRequest(id: number, payload: { reply?: string; resolved?: boolean }) {
  const { data } = await api.patch<AdminRequest>(`/api/admin-requests/${id}/`, payload)
  return data
}

export type TeacherRequest = { id: number; student: User; teaching_class: number; class_name: string; kind: 'REQUEST' | 'FEEDBACK'; subject: string; message: string; reply: string; resolved: boolean; created_at: string }
export async function listMyTeacherRequests() { const { data } = await api.get<TeacherRequest[]>('/api/my-teacher-requests/'); return data }
export async function sendTeacherRequest(payload: { class_id: number; kind: 'REQUEST' | 'FEEDBACK'; subject: string; message: string }) { const { data } = await api.post<TeacherRequest>('/api/my-teacher-requests/', payload); return data }
export async function listTeacherRequests(page: number, status = 'open') { const { data } = await api.get<{ count: number; results: TeacherRequest[] }>('/api/teacher-requests/', { params: { page, status } }); return data }
export async function updateTeacherRequest(id: number, payload: { reply?: string; resolved?: boolean }) { const { data } = await api.patch<TeacherRequest>(`/api/teacher-requests/${id}/`, payload); return data }
