import { api } from './client'
import type { User } from '../types/auth'
import type {
  CreateAdminPayload,
  CreateStudentPayload,
  CreateTeacherPayload,
  StudentProfile,
  TeacherProfile,
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

export async function createAdmin(payload: CreateAdminPayload): Promise<User> {
  const { data } = await api.post<User>('/api/users/admins/', payload)
  return data
}

export async function createTeacher(payload: CreateTeacherPayload): Promise<TeacherProfile> {
  const { data } = await api.post<TeacherProfile>('/api/teachers/', payload)
  return data
}

export async function createStudent(payload: CreateStudentPayload): Promise<StudentProfile> {
  const { data } = await api.post<StudentProfile>('/api/students/', payload)
  return data
}
