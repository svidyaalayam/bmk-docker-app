import { api } from './client'
import type { User } from '../types/auth'
import type {
  StudentProfile,
  TeacherProfile,
  UpdateStudentPayload,
  UpdateTeacherPayload,
} from '../types/school'

export async function listUsers(role?: string): Promise<User[]> {
  const { data } = await api.get<User[]>('/api/users/', {
    params: role ? { role } : undefined,
  })
  return data
}

export async function listStudents(): Promise<StudentProfile[]> {
  const { data } = await api.get<StudentProfile[]>('/api/students/')
  return data
}

export async function listTeachers(): Promise<TeacherProfile[]> {
  const { data } = await api.get<TeacherProfile[]>('/api/teachers/')
  return data
}

export async function updateTeacher(
  id: number,
  payload: UpdateTeacherPayload,
): Promise<TeacherProfile> {
  const { data } = await api.patch<TeacherProfile>(`/api/teachers/${id}/`, payload)
  return data
}

export async function updateStudent(
  id: number,
  payload: UpdateStudentPayload,
): Promise<StudentProfile> {
  const { data } = await api.patch<StudentProfile>(`/api/students/${id}/`, payload)
  return data
}
