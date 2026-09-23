import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  createComment,
  createSession,
  blockClassStudent,
  deleteComment,
  deleteSession,
  deleteSessionMaterial,
  getClass,
  listAttendance,
  listComments,
  listHomework,
  listSessionMaterials,
  startSession,
  updateAttendance,
  updateClass,
  updateComment,
  updateHomeworkFeedback,
  updateHomeworkSubmitted,
  updateSession,
  uploadHomework,
  uploadSessionMaterial,
} from '../api/classes'
import { useAuth } from '../auth/AuthContext'
import SiteHeader from '../components/SiteHeader'
import MediaCaptureUpload from '../components/MediaCaptureUpload'
import type {
  AttendanceRecord,
  AttendanceStatus,
  ClassSession,
  HomeworkSubmission,
  PersonBrief,
  SessionComment,
  SessionMaterial,
  SessionMaterialKind,
  TeachingClassDetail,
} from '../types/classes'
import { ATTENDANCE_LABELS } from '../types/classes'
import { getErrorMessage } from '../utils/errors'
import { myClassesPath } from '../utils/routes'

function personLabel(p: PersonBrief): string {
  const name = `${p.first_name || ''} ${p.last_name || ''}`.trim()
  const email = p.email || 'No email available'
  return name ? `${name} (${email})` : email
}

function personName(p: PersonBrief): string {
  return `${p.first_name || ''} ${p.last_name || ''}`.trim() || p.email || p.username
}

function personInitials(p: PersonBrief): string {
  const initials = `${p.first_name?.[0] || ''}${p.last_name?.[0] || ''}`.toUpperCase()
  if (initials) return initials
  return (p.username || p.email || '?').slice(0, 2).toUpperCase()
}

function formatSessionDate(isoDate: string): string {
  const d = new Date(`${isoDate}T00:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  return d.toLocaleDateString(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function isFutureSession(isoDate: string): boolean {
  const today = new Date()
  const todayIso = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, '0'),
    String(today.getDate()).padStart(2, '0'),
  ].join('-')
  return isoDate > todayIso
}

function presentSummary(present: number, total: number): string {
  if (total <= 0) return 'Present = 0/0'
  const pct = Math.round((present / total) * 100)
  return `Present = ${present}/${total} (${pct}%)`
}

function formatDateTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const ATTENDANCE_OPTIONS: {
  status: AttendanceStatus
  short: string
  className: string
  title: string
}[] = [
  { status: 'PRESENT', short: 'P', className: 'att-p', title: 'Present' },
  {
    status: 'AUTHORISED_ABSENT',
    short: 'AA',
    className: 'att-aa',
    title: 'Authorised absent',
  },
  {
    status: 'UNAUTHORISED_ABSENT',
    short: 'UA',
    className: 'att-ua',
    title: 'Unauthorised absent',
  },
  { status: 'NOT_MARKED', short: 'N', className: 'att-n', title: 'Not marked' },
]

export default function ClassDetailPage() {
  const { classId } = useParams()
  const id = Number(classId)
  const { user } = useAuth()
  const isTeacher = user?.role === 'TEACHER'
  const isStudent = user?.role === 'STUDENT'

  const [detail, setDetail] = useState<TeachingClassDetail | null>(null)
  const [description, setDescription] = useState('')
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null)
  const [newDate, setNewDate] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [savingDesc, setSavingDesc] = useState(false)
  const [blockingStudent, setBlockingStudent] = useState<PersonBrief | null>(null)
  const [blockReason, setBlockReason] = useState('')

  const refresh = useCallback(async () => {
    const data = await getClass(id)
    setDetail(data)
    setDescription(data.description || '')
    setSelectedSessionId((prev) => {
      if (prev && data.sessions.some((s) => s.id === prev)) return prev
      return null
    })
  }, [id])

  useEffect(() => {
    if (!Number.isFinite(id)) return
    refresh().catch((err) => setError(getErrorMessage(err, 'Could not load class.')))
  }, [id, refresh])

  if (!user) return null

  const selected = detail?.sessions.find((s) => s.id === selectedSessionId) || null

  const saveDescription = async (e: FormEvent) => {
    e.preventDefault()
    if (!isTeacher || !detail) return
    setSavingDesc(true)
    setError('')
    setMessage('')
    try {
      const updated = await updateClass(detail.id, { description })
      setDetail(updated)
      setMessage('Description saved.')
    } catch (err) {
      setError(getErrorMessage(err, 'Could not save description.'))
    } finally {
      setSavingDesc(false)
    }
  }

  const openBlockStudent = (student: PersonBrief) => {
    setBlockReason('absent for the last 3 consecutive classes.')
    setBlockingStudent(student)
  }

  const submitBlockStudent = async (e: FormEvent) => {
    e.preventDefault()
    if (!detail || !blockingStudent) return
    try {
      await blockClassStudent(detail.id, blockingStudent.id, blockReason)
      setBlockingStudent(null)
      setMessage(`${personName(blockingStudent)} has been blocked.`)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not block this student.'))
    }
  }

  const handleAddSession = async () => {
    if (!detail || !newDate) return
    try {
      await createSession(detail.id, { session_date: newDate })
      setNewDate('')
      setMessage('Session date added.')
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not add session.'))
    }
  }

  const handleDeleteSession = async (sessionId: number) => {
    const session = detail?.sessions.find((s) => s.id === sessionId)
    if (session?.is_started) {
      setError('Started sessions cannot be deleted.')
      return
    }
    if (!window.confirm('Delete this session date?')) return
    try {
      await deleteSession(sessionId)
      setMessage('Session deleted.')
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not delete session.'))
    }
  }

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="dash-shell wide">
        <header className="dash-header compact">
          <div>
            <p className="brand light">Class</p>
            <h1>{detail?.name || 'Loading…'}</h1>
            <p className="admin-cta">
              <Link to={myClassesPath(user.role)}>← My classes</Link>
            </p>
          </div>
        </header>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}

        {detail && (
          <>
            <section className="dash-panel">
              <h2>Details</h2>
              <p>
                <strong>Teacher 1:</strong> {personLabel(detail.teacher_1)}
                {detail.teacher_2 && (
                  <>
                    {' · '}
                    <strong>Teacher 2:</strong> {personLabel(detail.teacher_2)}
                  </>
                )}
              </p>

              {isTeacher ? (
                <form className="admin-form" onSubmit={saveDescription}>
                  <label className="full">
                    Description
                    <textarea
                      rows={4}
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                    />
                  </label>
                  <div className="form-actions">
                    <button type="submit" className="home-btn" disabled={savingDesc}>
                      {savingDesc ? 'Saving…' : 'Save description'}
                    </button>
                  </div>
                </form>
              ) : (
                <p className="header-sub">{detail.description || 'No description.'}</p>
              )}

              {isTeacher && (
                <>
                  <h3>Students ({detail.students.length})</h3>
                  <div className="table-wrap student-summary-table-wrap">
                    <table className="student-summary-table">
                      <thead>
                        <tr>
                          <th>Student</th>
                          <th>Attendance</th>
                          <th>Previous classes</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {detail.students.map((s) => (
                          <tr key={s.id}>
                            <td>
                              <div className="student-summary-person">
                                <span className="attendance-avatar" aria-hidden={!s.avatar_url}>
                                  {s.avatar_url ? (
                                    <img src={s.avatar_url} alt="" />
                                  ) : (
                                    personInitials(s)
                                  )}
                                </span>
                                <span>
                                  <strong>{personName(s)}</strong>
                                  {s.email && <span className="muted">{s.email}</span>}
                                </span>
                              </div>
                            </td>
                            <td>
                              {s.attendance_present ?? 0}/{s.attendance_total ?? 0}
                            </td>
                            <td>
                              <div className="recent-attendance-list">
                                {(s.attendance_recent || []).map((recent) => {
                                  if (!recent.status) {
                                    return (
                                      <span
                                        key={recent.date}
                                        className="att-legend recent-attendance-pill attendance-not-enrolled"
                                        title={`${formatSessionDate(recent.date)}: Student was not enrolled`}
                                      >
                                        —
                                      </span>
                                    )
                                  }
                                  const option = ATTENDANCE_OPTIONS.find(
                                    (item) => item.status === recent.status,
                                  ) || ATTENDANCE_OPTIONS[ATTENDANCE_OPTIONS.length - 1]
                                  return (
                                    <span
                                      key={recent.date}
                                      className={`att-legend recent-attendance-pill ${option.className}`}
                                      title={`${formatSessionDate(recent.date)}: ${option.title}`}
                                    >
                                      {option.short}
                                    </span>
                                  )
                                })}
                                {(!s.attendance_recent || s.attendance_recent.length === 0) && (
                                  <span className="muted">—</span>
                                )}
                              </div>
                            </td>
                            <td>
                              {s.account_blocked ? (
                                <span className="student-blocked-pill">Blocked</span>
                              ) : s.can_block ? (
                                <button
                                  type="button"
                                  className="home-btn danger"
                                  onClick={() => openBlockStudent(s)}
                                >
                                  Block
                                </button>
                              ) : null}
                            </td>
                          </tr>
                        ))}
                        {detail.students.length === 0 && (
                          <tr>
                            <td colSpan={4}>No students enrolled.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </section>

            <section className="dash-panel">
              <h2>Calendar</h2>
              {isTeacher && (
                <div className="inline-form">
                  <input
                    type="date"
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                  />
                  <button type="button" className="home-btn" onClick={handleAddSession}>
                    Add date
                  </button>
                </div>
              )}

              <div className="session-picker">
                {detail.sessions.map((s) => {
                  const present = s.present_count ?? 0
                  const total = s.attendance_total ?? 0
                  const myStatus = s.my_attendance_status
                  return (
                    <button
                      key={s.id}
                      type="button"
                      className={[
                        'session-chip',
                        selectedSessionId === s.id ? 'active' : '',
                        s.is_started ? 'started' : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() => setSelectedSessionId(s.id)}
                    >
                      <span className="session-chip-main">
                        <span className="session-chip-date">{formatSessionDate(s.session_date)}</span>
                        {s.is_started && isTeacher && (
                          <span className="session-chip-summary">
                            {presentSummary(present, total)}
                          </span>
                        )}
                        {s.is_started && isStudent && myStatus && (
                          <span className="session-chip-summary">
                            {ATTENDANCE_LABELS[myStatus]}
                          </span>
                        )}
                      </span>
                      {s.is_started && <span className="session-started-pill">Started</span>}
                    </button>
                  )
                })}
                {detail.sessions.length === 0 && (
                  <p className="header-sub">No calendar dates yet.</p>
                )}
              </div>

              {isTeacher && selected && !selected.is_started && (
                <button
                  type="button"
                  className="home-btn secondary"
                  onClick={() => handleDeleteSession(selected.id)}
                >
                  Delete selected date
                </button>
              )}
              {isTeacher && selected?.is_started && (
                <p className="header-sub">
                  This session has started — its date cannot be changed or deleted.
                </p>
              )}
            </section>

            {selected && (
              <SessionPanel
                session={selected}
                students={detail.students}
                isTeacher={!!isTeacher}
                isStudent={!!isStudent}
                onSessionUpdated={async () => {
                  await refresh()
                }}
                onMessage={setMessage}
                onError={setError}
              />
            )}
          </>
        )}
        {blockingStudent && (
          <div className="modal-backdrop" role="presentation" onClick={() => setBlockingStudent(null)}>
            <div
              className="dash-panel edit-user-modal block-student-modal"
              role="dialog"
              aria-modal="true"
              onClick={(e) => e.stopPropagation()}
            >
              <h2>Block student</h2>
              <p>Are you sure you want to block this student. Once Blocked only Admins can unblock</p>
              <form className="admin-form" onSubmit={submitBlockStudent}>
                <label>
                  Reason for blocking
                  <textarea
                    rows={4}
                    value={blockReason}
                    onChange={(e) => setBlockReason(e.target.value)}
                    required
                  />
                </label>
                <div className="form-actions">
                  <button type="button" className="tab" onClick={() => setBlockingStudent(null)}>
                    Cancel
                  </button>
                  <button type="submit" className="home-btn danger">
                    Block student
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function SessionPanel({
  session,
  students,
  isTeacher,
  isStudent,
  onSessionUpdated,
  onMessage,
  onError,
}: {
  session: ClassSession
  students: PersonBrief[]
  isTeacher: boolean
  isStudent: boolean
  onSessionUpdated: () => Promise<void>
  onMessage: (msg: string) => void
  onError: (msg: string) => void
}) {
  const [classwork, setClasswork] = useState(session.classwork || '')
  const [homework, setHomework] = useState(session.homework || '')
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([])
  const [focusStudentId, setFocusStudentId] = useState<number | null>(
    students[0]?.id ?? null,
  )
  const [comments, setComments] = useState<SessionComment[]>([])
  const [commentBody, setCommentBody] = useState('')
  const [homeworks, setHomeworks] = useState<HomeworkSubmission[]>([])
  const [materials, setMaterials] = useState<SessionMaterial[]>([])
  const [feedbackDrafts, setFeedbackDrafts] = useState<Record<number, string>>({})

  useEffect(() => {
    setClasswork(session.classwork || '')
    setHomework(session.homework || '')
  }, [session.id, session.classwork, session.homework])

  const loadSideData = useCallback(async () => {
    const [att, hw, mats] = await Promise.all([
      listAttendance(session.id),
      listHomework(session.id),
      listSessionMaterials(session.id),
    ])
    setAttendance(att)
    setHomeworks(hw)
    setMaterials(mats)
    setFeedbackDrafts(
      Object.fromEntries(hw.map((h) => [h.id, h.teacher_feedback || ''])),
    )
    if (isStudent) {
      const mine = await listComments(session.id)
      setComments(mine)
    }
  }, [session.id, isStudent])

  useEffect(() => {
    loadSideData().catch((err) => onError(getErrorMessage(err, 'Could not load session data.')))
  }, [loadSideData, onError])

  useEffect(() => {
    if (!isTeacher || focusStudentId == null) return
    listComments(session.id, focusStudentId)
      .then(setComments)
      .catch((err) => onError(getErrorMessage(err, 'Could not load comments.')))
  }, [isTeacher, focusStudentId, session.id, onError])

  const saveNotes = async () => {
    try {
      await updateSession(session.id, { classwork, homework })
      onMessage('Classwork / homework notes saved.')
      await onSessionUpdated()
    } catch (err) {
      onError(getErrorMessage(err, 'Could not save notes.'))
    }
  }

  const handleStart = async () => {
    try {
      await startSession(session.id)
      onMessage('Class started. Attendance rows created.')
      await onSessionUpdated()
      await loadSideData()
    } catch (err) {
      onError(getErrorMessage(err, 'Could not start class.'))
    }
  }

  const handleAttendance = async (recordId: number, status: AttendanceStatus) => {
    try {
      const updated = await updateAttendance(session.id, recordId, status)
      setAttendance((prev) => prev.map((r) => (r.id === recordId ? updated : r)))
      await onSessionUpdated()
    } catch (err) {
      onError(getErrorMessage(err, 'Could not update attendance.'))
    }
  }

  const markAllPresent = async () => {
    const pending = attendance.filter((row) => row.status !== 'PRESENT')
    if (pending.length === 0) {
      onMessage('All students are already marked present.')
      return
    }
    try {
      const updatedRows = await Promise.all(
        pending.map((row) => updateAttendance(session.id, row.id, 'PRESENT')),
      )
      const byId = new Map(updatedRows.map((r) => [r.id, r]))
      setAttendance((prev) => prev.map((r) => byId.get(r.id) || r))
      onMessage(`Marked ${pending.length} student${pending.length === 1 ? '' : 's'} present.`)
      await onSessionUpdated()
    } catch (err) {
      onError(getErrorMessage(err, 'Could not mark all present.'))
    }
  }

  const toggleHomeworkSubmitted = async (checked: boolean) => {
    const mine = attendance[0]
    if (!mine) return
    try {
      const updated = await updateHomeworkSubmitted(session.id, mine.id, checked)
      setAttendance([updated])
      onMessage(checked ? 'Marked homework as submitted.' : 'Homework submission cleared.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not update homework submission.'))
    }
  }

  const handleAddComment = async (e: FormEvent) => {
    e.preventDefault()
    if (!commentBody.trim()) return
    try {
      const created = await createComment(
        session.id,
        commentBody.trim(),
        isTeacher ? focusStudentId ?? undefined : undefined,
      )
      setComments((prev) => [...prev, created])
      setCommentBody('')
      onMessage('Comment added.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not add comment.'))
    }
  }

  const handleEditComment = async (comment: SessionComment) => {
    const next = window.prompt('Edit comment', comment.body)
    if (next == null || !next.trim()) return
    try {
      const updated = await updateComment(comment.id, next.trim())
      setComments((prev) => prev.map((c) => (c.id === comment.id ? updated : c)))
    } catch (err) {
      onError(getErrorMessage(err, 'Could not edit comment.'))
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    try {
      await deleteComment(commentId)
      setComments((prev) => prev.filter((c) => c.id !== commentId))
    } catch (err) {
      onError(getErrorMessage(err, 'Could not delete comment.'))
    }
  }

  const handleUpload = async (file: File | null) => {
    if (!file) return
    try {
      const hw = await uploadHomework(session.id, file)
      setHomeworks((prev) => [hw, ...prev])
      onMessage('Homework uploaded.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not upload homework.'))
      throw err
    }
  }

  const saveFeedback = async (homeworkId: number) => {
    try {
      const updated = await updateHomeworkFeedback(
        homeworkId,
        feedbackDrafts[homeworkId] || '',
      )
      setHomeworks((prev) => prev.map((h) => (h.id === homeworkId ? updated : h)))
      onMessage('Feedback saved.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not save feedback.'))
    }
  }

  const handleMaterialUpload = async (kind: SessionMaterialKind, file: File | null) => {
    if (!file) return
    try {
      const material = await uploadSessionMaterial(session.id, kind, file)
      setMaterials((prev) => [...prev, material])
      onMessage(`${kind === 'CLASSWORK' ? 'Classwork' : 'Homework'} file uploaded.`)
    } catch (err) {
      onError(getErrorMessage(err, 'Could not upload file.'))
      throw err
    }
  }

  const handleMaterialDelete = async (materialId: number) => {
    if (!window.confirm('Delete this file?')) return
    try {
      await deleteSessionMaterial(materialId)
      setMaterials((prev) => prev.filter((m) => m.id !== materialId))
      onMessage('File deleted.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not delete file.'))
    }
  }

  const classworkMaterials = materials.filter((m) => m.kind === 'CLASSWORK')
  const homeworkMaterials = materials.filter((m) => m.kind === 'HOMEWORK')

  return (
    <section className="dash-panel">
      <h2>Session {session.session_date}</h2>

      {(isTeacher || isStudent) && (
        <div className="form-grid">
          <label className="full">
            Classwork notes
            <textarea
              rows={3}
              value={classwork}
              onChange={(e) => setClasswork(e.target.value)}
              readOnly={!isTeacher}
            />
          </label>
          <div className="full material-block">
            <h3>Classwork files</h3>
            {isTeacher && (
              <MediaCaptureUpload
                label="Choose classwork file"
                maxBytes={20 * 1024 * 1024}
                onUpload={(file) => handleMaterialUpload('CLASSWORK', file)}
              />
            )}
            <ul className="material-list">
              {classworkMaterials.map((m) => (
                <li key={m.id}>
                  {m.file_url ? (
                    <a href={m.file_url} target="_blank" rel="noreferrer">
                      {m.original_filename || 'View file'}
                    </a>
                  ) : (
                    m.original_filename || 'File'
                  )}
                  {isTeacher && (
                    <button
                      type="button"
                      className="home-btn danger"
                      onClick={() => handleMaterialDelete(m.id)}
                    >
                      Delete
                    </button>
                  )}
                </li>
              ))}
              {classworkMaterials.length === 0 && (
                <li className="header-sub">No classwork files yet.</li>
              )}
            </ul>
          </div>

          <label className="full">
            Homework notes
            <textarea
              rows={3}
              value={homework}
              onChange={(e) => setHomework(e.target.value)}
              readOnly={!isTeacher}
            />
          </label>
          <div className="full material-block">
            <h3>Homework files (from teacher)</h3>
            {isTeacher && (
              <MediaCaptureUpload
                label="Choose homework file"
                maxBytes={20 * 1024 * 1024}
                onUpload={(file) => handleMaterialUpload('HOMEWORK', file)}
              />
            )}
            <ul className="material-list">
              {homeworkMaterials.map((m) => (
                <li key={m.id}>
                  {m.file_url ? (
                    <a href={m.file_url} target="_blank" rel="noreferrer">
                      {m.original_filename || 'View file'}
                    </a>
                  ) : (
                    m.original_filename || 'File'
                  )}
                  {isTeacher && (
                    <button
                      type="button"
                      className="home-btn danger"
                      onClick={() => handleMaterialDelete(m.id)}
                    >
                      Delete
                    </button>
                  )}
                </li>
              ))}
              {homeworkMaterials.length === 0 && (
                <li className="header-sub">No homework files yet.</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {isTeacher && (
        <div className="form-actions">
          <button type="button" className="home-btn" onClick={saveNotes}>
            Save notes
          </button>
          {session.is_started ? (
            <span className="session-started-pill large">Started</span>
          ) : (
            <>
              <button
                type="button"
                className="home-btn"
                onClick={handleStart}
                disabled={isFutureSession(session.session_date)}
                title={
                  isFutureSession(session.session_date)
                    ? 'This class can be started on or after its date.'
                    : undefined
                }
              >
                Start class
              </button>
              {isFutureSession(session.session_date) && (
                <span className="header-sub">
                  This class can be started on or after its scheduled date.
                </span>
              )}
            </>
          )}
        </div>
      )}

      {isTeacher && session.is_started && (
        <>
          <div className="attendance-toolbar">
            <div>
              <h3>Attendance</h3>
              <p className="attendance-summary">
                {presentSummary(
                  attendance.filter((r) => r.status === 'PRESENT').length,
                  attendance.length,
                )}
              </p>
            </div>
            <button type="button" className="home-btn" onClick={markAllPresent}>
              Mark all present
            </button>
          </div>
          <p className="attendance-legend">
            <span className="att-legend att-p">P Present</span>
            <span className="att-legend att-aa">AA Authorised absent</span>
            <span className="att-legend att-ua">UA Unauthorised absent</span>
            <span className="att-legend att-n">N Not marked</span>
          </p>
          <ul className="attendance-list">
            {attendance.map((row) => (
              <li key={row.id} className="attendance-row">
                <div
                  className="attendance-radios"
                  role="radiogroup"
                  aria-label={`Attendance for ${personLabel(row.student)}`}
                >
                  {ATTENDANCE_OPTIONS.map((opt) => (
                    <label
                      key={opt.status}
                      className={`att-radio ${opt.className}${row.status === opt.status ? ' selected' : ''}`}
                      title={opt.title}
                    >
                      <input
                        type="radio"
                        name={`attendance-${row.id}`}
                        value={opt.status}
                        checked={row.status === opt.status}
                        onChange={() => handleAttendance(row.id, opt.status)}
                      />
                      <span>{opt.short}</span>
                    </label>
                  ))}
                </div>
                <span
                  className={`hw-mark${row.homework_submitted ? ' submitted' : ' missing'}`}
                  title={
                    row.homework_submitted
                      ? 'Homework submitted'
                      : 'Homework not submitted'
                  }
                >
                  {row.homework_submitted ? 'HW ✓' : 'HW ✕'}
                </span>
                <button
                  type="button"
                  className={`attendance-name${focusStudentId === row.student.id ? ' selected' : ''}`}
                  onClick={() => setFocusStudentId(row.student.id)}
                >
                  <span className="attendance-avatar" aria-hidden={!row.student.avatar_url}>
                    {row.student.avatar_url ? (
                      <img src={row.student.avatar_url} alt="" />
                    ) : (
                      personInitials(row.student)
                    )}
                  </span>
                  <span>{personLabel(row.student)}</span>
                </button>
              </li>
            ))}
            {attendance.length === 0 && (
              <li className="header-sub">No attendance rows yet.</li>
            )}
          </ul>
        </>
      )}

      {isStudent && session.is_started && attendance[0] && (
        <div className="student-session-status">
          <p>
            <strong>Your attendance:</strong> {ATTENDANCE_LABELS[attendance[0].status]}
          </p>
          <label className="hw-submit-check">
            <input
              type="checkbox"
              checked={Boolean(attendance[0].homework_submitted)}
              onChange={(e) => toggleHomeworkSubmitted(e.target.checked)}
            />
            Homework submitted
          </label>
        </div>
      )}

      {isStudent && !session.is_started && (
        <p className="header-sub">Attendance and homework submission open after the class is started.</p>
      )}

      {session.is_started ? (
        <>
          <h3>
            Communication
            {isTeacher && focusStudentId != null && (
              <span className="muted">
                {' '}
                —{' '}
                {personLabel(
                  students.find((s) => s.id === focusStudentId) || {
                    id: 0,
                    username: 'student',
                    first_name: '',
                    last_name: '',
                  },
                )}
              </span>
            )}
          </h3>

          {isTeacher && (
            <label>
              Student for communication
              <select
                value={focusStudentId ?? ''}
                onChange={(e) => setFocusStudentId(Number(e.target.value))}
              >
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {personLabel(s)}
                  </option>
                ))}
              </select>
            </label>
          )}

          <ul className="comment-list">
            {comments.map((c) => (
              <li key={c.id}>
                <div className="comment-meta">
                  <strong>{c.author_name}</strong>
                  <span className="muted"> ({c.author_role})</span>
                  <time className="comment-time" dateTime={c.created_at}>
                    {formatDateTime(c.created_at)}
                  </time>
                </div>
                <p>{c.body}</p>
                {c.can_edit && (
                  <div className="inline-form">
                    <button
                      type="button"
                      className="home-btn secondary"
                      onClick={() => handleEditComment(c)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="home-btn secondary"
                      onClick={() => handleDeleteComment(c.id)}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </li>
            ))}
            {comments.length === 0 && <li className="header-sub">No messages yet.</li>}
          </ul>

          <form className="admin-form" onSubmit={handleAddComment}>
            <label className="full">
              Add message
              <textarea
                rows={2}
                value={commentBody}
                onChange={(e) => setCommentBody(e.target.value)}
                required
              />
            </label>
            <button type="submit" className="home-btn">
              Post message
            </button>
          </form>
        </>
      ) : (
        <p className="header-sub">
          Communication becomes available after the class is started.
        </p>
      )}

      <h3>Student's homework submissions</h3>
      {isStudent && session.is_started && (
        <MediaCaptureUpload
          label="Choose homework file"
          maxBytes={10 * 1024 * 1024}
          onUpload={handleUpload}
        />
      )}
      {isStudent && !session.is_started && (
        <p className="header-sub">
          Homework submission opens after the class is started.
        </p>
      )}

      <ul className="homework-list">
        {homeworks.map((hw) => (
          <li key={hw.id}>
            <div>
              {isTeacher && <strong>{personLabel(hw.student)} — </strong>}
              {hw.file_url ? (
                <a href={hw.file_url} target="_blank" rel="noreferrer">
                  {hw.original_filename || 'View file'}
                </a>
              ) : (
                hw.original_filename || 'File'
              )}
              <span className="muted"> ({hw.storage_backend})</span>
            </div>
            {isTeacher ? (
              <div className="feedback-block">
                <textarea
                  rows={2}
                  value={feedbackDrafts[hw.id] || ''}
                  onChange={(e) =>
                    setFeedbackDrafts((prev) => ({ ...prev, [hw.id]: e.target.value }))
                  }
                  placeholder="Teacher feedback"
                />
                <button type="button" className="home-btn" onClick={() => saveFeedback(hw.id)}>
                  Save feedback
                </button>
              </div>
            ) : (
              <p className="header-sub">
                Feedback: {hw.teacher_feedback || 'None yet.'}
              </p>
            )}
          </li>
        ))}
        {homeworks.length === 0 && <li className="header-sub">No homework uploaded yet.</li>}
      </ul>
    </section>
  )
}
