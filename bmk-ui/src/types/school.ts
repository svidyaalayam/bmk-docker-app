import type { User } from './auth'

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

export interface UpdateTeacherPayload {
  first_name?: string
  last_name?: string
  email?: string
  phone_number?: string | null
  gender?: Gender
  phone?: string
  is_active?: boolean
}

export interface UpdateStudentPayload {
  first_name?: string
  last_name?: string
  email?: string
  phone_number?: string | null
  gender?: Gender
  date_of_birth?: string | null
  phone?: string
  parent_name?: string
  parent_phone?: string
  address?: string
  notes?: string
  is_active?: boolean
}
