export type UserRole = 'ADMIN' | 'TEACHER' | 'STUDENT'
export type LessonApp = 'sikshavahini' | 'sunaadam'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  phone_number: string | null
  school_id: number | null
  school_slug: string | null
  school_name: string | null
  lesson_app: LessonApp | null
  email_verified?: boolean
  is_active?: boolean
  profile_locked?: boolean
  legacy_uid?: string | null
  date_joined?: string
  last_login?: string | null
  avatar_url?: string | null
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface DashboardPayload {
  dashboard: string
  message: string
  capabilities: string[]
  pending_activations?: number
  account_blocked?: boolean
  block_reason?: string
}
