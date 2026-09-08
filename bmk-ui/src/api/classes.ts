import { api } from './client'
import type {
  AttendanceRecord,
  AttendanceStatus,
  ClassSession,
  CreateClassPayload,
  HomeworkSubmission,
  SessionComment,
  SessionMaterial,
  SessionMaterialKind,
  TeachingClassDetail,
  TeachingClassListItem,
  UpdateClassPayload,
} from '../types/classes'

export async function listClasses(): Promise<TeachingClassListItem[]> {
  const { data } = await api.get<TeachingClassListItem[]>('/api/classes/')
  return data
}

export async function getClass(id: number): Promise<TeachingClassDetail> {
  const { data } = await api.get<TeachingClassDetail>(`/api/classes/${id}/`)
  return data
}

export async function createClass(payload: CreateClassPayload): Promise<TeachingClassDetail> {
  const { data } = await api.post<TeachingClassDetail>('/api/classes/', payload)
  return data
}

export async function updateClass(
  id: number,
  payload: UpdateClassPayload,
): Promise<TeachingClassDetail> {
  const { data } = await api.patch<TeachingClassDetail>(`/api/classes/${id}/`, payload)
  return data
}

export async function deleteClass(id: number): Promise<void> {
  await api.delete(`/api/classes/${id}/`)
}

export async function addClassStudents(id: number, studentIds: number[]): Promise<void> {
  await api.post(`/api/classes/${id}/students/`, { student_ids: studentIds })
}

export async function removeClassStudent(classId: number, studentId: number): Promise<void> {
  await api.delete(`/api/classes/${classId}/students/${studentId}/`)
}

export async function listSessions(classId: number): Promise<ClassSession[]> {
  const { data } = await api.get<ClassSession[]>(`/api/classes/${classId}/sessions/`)
  return data
}

export async function createSession(
  classId: number,
  payload: { session_date: string; classwork?: string; homework?: string },
): Promise<ClassSession> {
  const { data } = await api.post<ClassSession>(`/api/classes/${classId}/sessions/`, payload)
  return data
}

export async function importCalendarDates(
  classId: number,
  dates: string[],
): Promise<{ created_count: number; skipped_count: number; created: ClassSession[] }> {
  const { data } = await api.post(`/api/classes/${classId}/calendar/import/`, { dates })
  return data
}

export async function updateSession(
  sessionId: number,
  payload: { session_date?: string; classwork?: string; homework?: string },
): Promise<ClassSession> {
  const { data } = await api.patch<ClassSession>(`/api/sessions/${sessionId}/`, payload)
  return data
}

export async function deleteSession(sessionId: number): Promise<void> {
  await api.delete(`/api/sessions/${sessionId}/`)
}

export async function startSession(sessionId: number): Promise<ClassSession> {
  const { data } = await api.post<ClassSession>(`/api/sessions/${sessionId}/start/`)
  return data
}

export async function listAttendance(sessionId: number): Promise<AttendanceRecord[]> {
  const { data } = await api.get<AttendanceRecord[]>(`/api/sessions/${sessionId}/attendance/`)
  return data
}

export async function updateAttendance(
  sessionId: number,
  attendanceId: number,
  status: AttendanceStatus,
): Promise<AttendanceRecord> {
  const { data } = await api.patch<AttendanceRecord>(
    `/api/sessions/${sessionId}/attendance/${attendanceId}/`,
    { status },
  )
  return data
}

export async function updateHomeworkSubmitted(
  sessionId: number,
  attendanceId: number,
  homeworkSubmitted: boolean,
): Promise<AttendanceRecord> {
  const { data } = await api.patch<AttendanceRecord>(
    `/api/sessions/${sessionId}/attendance/${attendanceId}/`,
    { homework_submitted: homeworkSubmitted },
  )
  return data
}

export async function listComments(
  sessionId: number,
  studentId?: number,
): Promise<SessionComment[]> {
  const { data } = await api.get<SessionComment[]>(`/api/sessions/${sessionId}/comments/`, {
    params: studentId ? { student: studentId } : undefined,
  })
  return data
}

export async function createComment(
  sessionId: number,
  body: string,
  studentId?: number,
): Promise<SessionComment> {
  const { data } = await api.post<SessionComment>(`/api/sessions/${sessionId}/comments/`, {
    body,
    ...(studentId != null ? { student_id: studentId } : {}),
  })
  return data
}

export async function updateComment(commentId: number, body: string): Promise<SessionComment> {
  const { data } = await api.patch<SessionComment>(`/api/comments/${commentId}/`, { body })
  return data
}

export async function deleteComment(commentId: number): Promise<void> {
  await api.delete(`/api/comments/${commentId}/`)
}

export async function listHomework(sessionId: number): Promise<HomeworkSubmission[]> {
  const { data } = await api.get<HomeworkSubmission[]>(`/api/sessions/${sessionId}/homework/`)
  return data
}

export async function uploadHomework(sessionId: number, file: File): Promise<HomeworkSubmission> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<HomeworkSubmission>(
    `/api/sessions/${sessionId}/homework/`,
    form,
  )
  return data
}

export async function updateHomeworkFeedback(
  homeworkId: number,
  teacherFeedback: string,
): Promise<HomeworkSubmission> {
  const { data } = await api.patch<HomeworkSubmission>(`/api/homework/${homeworkId}/`, {
    teacher_feedback: teacherFeedback,
  })
  return data
}

export async function listSessionMaterials(
  sessionId: number,
  kind?: SessionMaterialKind,
): Promise<SessionMaterial[]> {
  const { data } = await api.get<SessionMaterial[]>(`/api/sessions/${sessionId}/materials/`, {
    params: kind ? { kind } : undefined,
  })
  return data
}

export async function uploadSessionMaterial(
  sessionId: number,
  kind: SessionMaterialKind,
  file: File,
): Promise<SessionMaterial> {
  const form = new FormData()
  form.append('kind', kind)
  form.append('file', file)
  const { data } = await api.post<SessionMaterial>(
    `/api/sessions/${sessionId}/materials/`,
    form,
  )
  return data
}

export async function deleteSessionMaterial(materialId: number): Promise<void> {
  await api.delete(`/api/materials/${materialId}/`)
}
