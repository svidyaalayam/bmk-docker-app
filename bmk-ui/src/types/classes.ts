export type AttendanceStatus =
  | 'NOT_MARKED'
  | 'PRESENT'
  | 'AUTHORISED_ABSENT'
  | 'UNAUTHORISED_ABSENT'

export interface PersonBrief {
  id: number
  username: string
  first_name: string
  last_name: string
  email?: string
  avatar_url?: string | null
  account_blocked?: boolean
  attendance_present?: number
  attendance_total?: number
  attendance_recent?: Array<{ date: string; status: AttendanceStatus | null }>
  can_block?: boolean
}

export interface ClassSession {
  id: number
  teaching_class: number
  session_date: string
  classwork: string
  homework: string
  is_started: boolean
  started_at: string | null
  present_count?: number | null
  attendance_total?: number | null
  my_attendance_status?: AttendanceStatus | null
  created_at: string
  updated_at: string
}

export interface TeachingClassListItem {
  id: number
  name: string
  description: string
  teacher_1: PersonBrief
  teacher_2: PersonBrief | null
  student_count: number
  session_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TeachingClassDetail {
  id: number
  name: string
  description: string
  teacher_1: PersonBrief
  teacher_2: PersonBrief | null
  students: PersonBrief[]
  sessions: ClassSession[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateClassPayload {
  name: string
  description?: string
  teacher_1_id: number
  teacher_2_id?: number | null
  student_ids?: number[]
}

export interface UpdateClassPayload {
  name?: string
  description?: string
  teacher_1_id?: number
  teacher_2_id?: number | null
  student_ids?: number[]
}

export interface AttendanceRecord {
  id: number
  session: number
  student: PersonBrief
  status: AttendanceStatus
  homework_submitted: boolean
  updated_at: string
}

export interface SessionComment {
  id: number
  session: number
  student: number
  author: number
  author_username: string
  author_role: string
  author_name: string
  body: string
  can_edit: boolean
  created_at: string
  updated_at: string
}

export interface HomeworkSubmission {
  id: number
  session: number
  student: PersonBrief
  original_filename: string
  content_type: string
  file_url: string | null
  storage_backend: string
  storage_uri: string
  teacher_feedback: string
  ai_evaluation_status: string
  ai_evaluation_notes: string
  created_at: string
  updated_at: string
}

export type SessionMaterialKind = 'CLASSWORK' | 'HOMEWORK'

export interface SessionMaterial {
  id: number
  session: number
  kind: SessionMaterialKind
  original_filename: string
  content_type: string
  file_url: string | null
  created_at: string
  updated_at: string
}

export const ATTENDANCE_LABELS: Record<AttendanceStatus, string> = {
  NOT_MARKED: 'Not marked',
  PRESENT: 'Present',
  AUTHORISED_ABSENT: 'Authorised absent',
  UNAUTHORISED_ABSENT: 'Unauthorised absent',
}
