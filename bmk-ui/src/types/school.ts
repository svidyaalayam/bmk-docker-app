import type { User, UserRole } from './auth'

export type Gender = 'M' | 'F' | 'O'

export interface StudentProfile {
  id: number
  user: User
  gender: Gender
  date_of_birth: string | null
  phone: string
  parent_name: string
  parent_phone: string
  address: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TeacherProfile {
  id: number
  user: User
  gender: Gender
  phone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateAdminPayload {
  username: string
  password: string
  email?: string
  first_name?: string
  last_name?: string
  phone_number?: string
}

export interface CreateTeacherPayload extends CreateAdminPayload {
  gender: Gender
  phone?: string
}

export interface CreateStudentPayload extends CreateAdminPayload {
  gender: Gender
  date_of_birth?: string | null
  phone?: string
  parent_name?: string
  parent_phone?: string
  address?: string
  notes?: string
}

export type CreateRole = Extract<UserRole, 'ADMIN' | 'TEACHER' | 'STUDENT'>
