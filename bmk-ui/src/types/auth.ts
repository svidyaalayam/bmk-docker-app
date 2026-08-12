export type UserRole = 'ADMIN' | 'TEACHER' | 'STUDENT'

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
  email_verified?: boolean
  is_active?: boolean
  profile_locked?: boolean
  date_joined?: string
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
}
