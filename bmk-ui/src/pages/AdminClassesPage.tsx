import { useEffect, useMemo, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  createClass,
  createSession,
  deleteClass,
  deleteSession,
  getClass,
  importCalendarDates,
  listClasses,
  updateClass,
  updateSession,
} from '../api/classes'
import { listStudents, listTeachers } from '../api/school'
import DataTable, { type DataTableColumn } from '../components/DataTable'
import SiteHeader from '../components/SiteHeader'
import type { TeachingClassDetail, TeachingClassListItem } from '../types/classes'
import type { StudentProfile, TeacherProfile } from '../types/school'
import { getErrorMessage } from '../utils/errors'
import { adminClassesPath, dashboardPathForRole } from '../utils/routes'

function personLabel(p: { first_name: string; last_name: string; username: string }): string {
  const name = `${p.first_name || ''} ${p.last_name || ''}`.trim()
  return name ? `${name} (${p.username})` : p.username
}

export default function AdminClassesPage() {
  const [classes, setClasses] = useState<TeachingClassListItem[]>([])
  const [teachers, setTeachers] = useState<TeacherProfile[]>([])
  const [students, setStudents] = useState<StudentProfile[]>([])
  const [editingId, setEditingId] = useState<number | 'new' | null>(null)
  const [detail, setDetail] = useState<TeachingClassDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const refresh = async () => {
    const [classData, teacherData, studentData] = await Promise.all([
      listClasses(),
      listTeachers(),
      listStudents(),
    ])
    setClasses(classData)
    setTeachers(teacherData)
    setStudents(studentData)
  }

  useEffect(() => {
    refresh().catch(() => setError('Could not load class management data.'))
  }, [])

  const openCreate = () => {
    setMessage('')
    setError('')
    setDetail(null)
    setEditingId('new')
  }

  const openEdit = async (id: number) => {
    setMessage('')
    setError('')
    setLoading(true)
    try {
      const data = await getClass(id)
      setDetail(data)
      setEditingId(id)
    } catch (err) {
      setError(getErrorMessage(err, 'Could not load class.'))
    } finally {
      setLoading(false)
    }
  }

  const columns = useMemo<DataTableColumn<TeachingClassListItem>[]>(
    () => [
      { key: 'name', header: 'Class', getValue: (c) => c.name },
      {
        key: 'teacher1',
        header: 'Teacher 1',
        getValue: (c) => personLabel(c.teacher_1),
      },
      {
        key: 'teacher2',
        header: 'Teacher 2',
        getValue: (c) => (c.teacher_2 ? personLabel(c.teacher_2) : '—'),
      },
      {
        key: 'students',
        header: 'Students',
        getValue: (c) => String(c.student_count),
      },
      {
        key: 'sessions',
        header: 'Sessions',
        getValue: (c) => String(c.session_count),
      },
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (c) => (
          <button type="button" className="home-btn" onClick={() => openEdit(c.id)}>
            Edit
          </button>
        ),
      },
    ],
    [],
  )

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="dash-shell wide">
        <header className="dash-header compact">
          <div>
            <p className="brand light">Administration</p>
            <h1>Class Management</h1>
            <p className="header-sub">
              Create classes, assign teachers and students, and manage the session calendar.
            </p>
            <p className="admin-cta">
              <Link to={dashboardPathForRole('ADMIN')}>← Dashboard</Link>
              {' · '}
              <Link to={adminClassesPath()}>Class management</Link>
            </p>
          </div>
          <button type="button" className="home-btn" onClick={openCreate}>
            Add class
          </button>
        </header>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        {loading && <p className="header-sub">Loading…</p>}

        <section className="dash-panel">
          <h2>Classes ({classes.length})</h2>
          <DataTable
            rows={classes}
            columns={columns}
            rowKey={(c) => c.id}
            emptyMessage="No classes yet."
            searchPlaceholder="Filter classes…"
          />
        </section>

        {editingId !== null && (
          <div className="modal-backdrop" role="presentation" onClick={() => { setEditingId(null); setDetail(null) }}>
            <div
              className="dash-panel edit-user-modal class-editor-modal"
              role="dialog"
              aria-modal="true"
              onClick={(e) => e.stopPropagation()}
            >
              <ClassEditor
                mode={editingId === 'new' ? 'create' : 'edit'}
                detail={detail}
                teachers={teachers}
                students={students}
                onClose={() => {
                  setEditingId(null)
                  setDetail(null)
                }}
                onSaved={async (msg) => {
                  setMessage(msg)
                  setEditingId(null)
                  setDetail(null)
                  await refresh()
                }}
                onError={(msg) => setError(msg)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ClassEditor({
  mode,
  detail,
  teachers,
  students,
  onClose,
  onSaved,
  onError,
}: {
  mode: 'create' | 'edit'
  detail: TeachingClassDetail | null
  teachers: TeacherProfile[]
  students: StudentProfile[]
  onClose: () => void
  onSaved: (message: string) => Promise<void>
  onError: (message: string) => void
}) {
  const [name, setName] = useState(detail?.name || '')
  const [description, setDescription] = useState(detail?.description || '')
  const [teacher1Id, setTeacher1Id] = useState(detail?.teacher_1.id || teachers[0]?.id || 0)
  const [teacher2Id, setTeacher2Id] = useState<number | ''>(detail?.teacher_2?.id || '')
  const [teacherError, setTeacherError] = useState('')
  const [selectedStudents, setSelectedStudents] = useState<number[]>(
    detail?.students.map((s) => s.id) || [],
  )
  const [studentFilter, setStudentFilter] = useState('')
  const [sessions, setSessions] = useState(() =>
    [...(detail?.sessions || [])].sort((a, b) => a.session_date.localeCompare(b.session_date)),
  )
  const [newDate, setNewDate] = useState('')
  const [calendarError, setCalendarError] = useState('')
  const [calendarMessage, setCalendarMessage] = useState('')
  const [importingCalendar, setImportingCalendar] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const calendarFileRef = useRef<HTMLInputElement>(null)

  const studentById = useMemo(() => {
    const map = new Map<number, StudentProfile>()
    for (const s of students) map.set(s.id, s)
    return map
  }, [students])

  const selectedSet = useMemo(() => new Set(selectedStudents), [selectedStudents])

  const availableStudents = useMemo(() => {
    const q = studentFilter.trim().toLowerCase()
    return students
      .filter((s) => !selectedSet.has(s.id))
      .filter((s) => {
        if (!q) return true
        const label = personLabel(s.user).toLowerCase()
        const email = (s.user.email || '').toLowerCase()
        return label.includes(q) || email.includes(q)
      })
      .sort((a, b) => personLabel(a.user).localeCompare(personLabel(b.user)))
  }, [students, selectedSet, studentFilter])

  const enrolledStudents = useMemo(() => {
    return selectedStudents
      .map((id) => studentById.get(id))
      .filter((s): s is StudentProfile => Boolean(s))
      .sort((a, b) => personLabel(a.user).localeCompare(personLabel(b.user)))
  }, [selectedStudents, studentById])

  const teacher2Options = useMemo(
    () => teachers.filter((t) => t.id !== teacher1Id),
    [teachers, teacher1Id],
  )

  const selectTeacher1 = (id: number) => {
    setTeacher1Id(id)
    setTeacherError('')
    if (teacher2Id && teacher2Id === id) {
      setTeacher2Id('')
      setTeacherError('Teacher 2 must be different from Teacher 1. Selection cleared.')
    }
  }

  const selectTeacher2 = (value: string) => {
    const id = value ? Number(value) : ''
    if (id && id === teacher1Id) {
      setTeacherError('Teacher 2 must be different from Teacher 1.')
      setTeacher2Id('')
      return
    }
    setTeacherError('')
    setTeacher2Id(id)
  }

  const addStudent = (id: number) => {
    setSelectedStudents((prev) => (prev.includes(id) ? prev : [...prev, id]))
  }

  const removeStudent = (id: number) => {
    setSelectedStudents((prev) => prev.filter((x) => x !== id))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!teacher1Id) {
      onError('Teacher 1 is required.')
      return
    }
    if (teacher2Id && teacher2Id === teacher1Id) {
      setTeacherError('Teacher 2 must be different from Teacher 1.')
      onError('Teacher 2 must be different from Teacher 1.')
      return
    }
    setSubmitting(true)
    try {
      if (mode === 'create') {
        await createClass({
          name,
          description,
          teacher_1_id: teacher1Id,
          teacher_2_id: teacher2Id || null,
          student_ids: selectedStudents,
        })
        await onSaved('Class created.')
      } else if (detail) {
        await updateClass(detail.id, {
          name,
          description,
          teacher_1_id: teacher1Id,
          teacher_2_id: teacher2Id || null,
          student_ids: selectedStudents,
        })
        await onSaved('Class updated.')
      }
    } catch (err) {
      onError(getErrorMessage(err, 'Could not save class.'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!detail || !window.confirm(`Delete class “${detail.name}”?`)) return
    setSubmitting(true)
    try {
      await deleteClass(detail.id)
      await onSaved('Class deleted.')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not delete class.'))
    } finally {
      setSubmitting(false)
    }
  }

  const dateExists = (date: string, exceptSessionId?: number) =>
    sessions.some((s) => s.session_date === date && s.id !== exceptSessionId)

  const handleAddSession = async () => {
    if (!detail || !newDate) return
    setCalendarError('')
    if (dateExists(newDate)) {
      setCalendarError(`Date ${newDate} is already on this class calendar.`)
      return
    }
    try {
      const session = await createSession(detail.id, { session_date: newDate })
      setSessions((prev) =>
        [...prev, session].sort((a, b) => a.session_date.localeCompare(b.session_date)),
      )
      setNewDate('')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not add session date.'))
    }
  }

  const handleSessionDateChange = async (sessionId: number, sessionDate: string) => {
    const current = sessions.find((s) => s.id === sessionId)
    if (current?.is_started) {
      onError('Started sessions cannot change date.')
      return
    }
    setCalendarError('')
    if (dateExists(sessionDate, sessionId)) {
      setCalendarError(`Date ${sessionDate} is already on this class calendar.`)
      return
    }
    try {
      const updated = await updateSession(sessionId, { session_date: sessionDate })
      setSessions((prev) =>
        prev
          .map((s) => (s.id === sessionId ? updated : s))
          .sort((a, b) => a.session_date.localeCompare(b.session_date)),
      )
    } catch (err) {
      onError(getErrorMessage(err, 'Could not update session date.'))
    }
  }

  const handleDeleteSession = async (sessionId: number) => {
    const current = sessions.find((s) => s.id === sessionId)
    if (current?.is_started) {
      onError('Started sessions cannot be deleted.')
      return
    }
    if (!window.confirm('Delete this session date?')) return
    try {
      await deleteSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.id !== sessionId))
      setCalendarError('')
    } catch (err) {
      onError(getErrorMessage(err, 'Could not delete session.'))
    }
  }

  const handleExportCalendar = () => {
    const dates = sessions.map((session) => session.session_date)
    const payload = { dates }
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `${detail?.name || 'class'}-calendar-dates.json`.replace(/[^a-z0-9._-]/gi, '-')
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleImportCalendar = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !detail) return
    setCalendarError('')
    setCalendarMessage('')
    setImportingCalendar(true)
    try {
      const parsed: unknown = JSON.parse(await file.text())
      const dates =
        typeof parsed === 'object' && parsed !== null && Array.isArray((parsed as { dates?: unknown }).dates)
          ? (parsed as { dates: unknown[] }).dates
          : null
      if (!dates || !dates.every((date) => typeof date === 'string')) {
        throw new Error('Choose a calendar JSON file exported from this page.')
      }
      const result = await importCalendarDates(detail.id, dates)
      setSessions((previous) =>
        [...previous, ...result.created].sort((a, b) => a.session_date.localeCompare(b.session_date)),
      )
      setCalendarMessage(
        `Calendar import complete: ${result.created_count} date${result.created_count === 1 ? '' : 's'} added; ${result.skipped_count} existing or duplicate date${result.skipped_count === 1 ? '' : 's'} left unchanged.`,
      )
    } catch (err) {
      setCalendarError(err instanceof Error ? err.message : getErrorMessage(err, 'Could not import calendar dates.'))
    } finally {
      if (calendarFileRef.current) calendarFileRef.current.value = ''
      setImportingCalendar(false)
    }
  }

  return (
    <>
      <header className="modal-header">
        <h2>{mode === 'create' ? 'Add class' : 'Edit class'}</h2>
        <button type="button" className="home-btn secondary" onClick={onClose}>
          Close
        </button>
      </header>

      <form className="admin-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label className="full">
            Description
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>
          <label>
            Teacher 1 (required)
            <select
              value={teacher1Id || ''}
              onChange={(e) => selectTeacher1(Number(e.target.value))}
              required
            >
              <option value="">Select…</option>
              {teachers.map((t) => (
                <option key={t.id} value={t.id}>
                  {personLabel(t.user)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Teacher 2 (optional)
            <select value={teacher2Id} onChange={(e) => selectTeacher2(e.target.value)}>
              <option value="">None</option>
              {teacher2Options.map((t) => (
                <option key={t.id} value={t.id}>
                  {personLabel(t.user)}
                </option>
              ))}
            </select>
          </label>
        </div>
        {teacherError && <p className="error">{teacherError}</p>}

        <h3>Students</h3>
        <p className="header-sub">
          Click a name on the left to enrol them, or on the right to remove them.
        </p>
        <div className="student-transfer">
          <div className="student-transfer-col">
            <div className="student-transfer-head">
              <strong>Available ({availableStudents.length})</strong>
              <input
                type="search"
                placeholder="Filter students…"
                value={studentFilter}
                onChange={(e) => setStudentFilter(e.target.value)}
                aria-label="Filter available students"
              />
            </div>
            <ul className="student-transfer-list">
              {availableStudents.map((s) => (
                <li key={s.id}>
                  <button type="button" className="student-transfer-item" onClick={() => addStudent(s.id)}>
                    {personLabel(s.user)}
                    <span className="muted">Add →</span>
                  </button>
                </li>
              ))}
              {availableStudents.length === 0 && (
                <li className="header-sub">
                  {studentFilter.trim()
                    ? 'No matching students.'
                    : students.length === 0
                      ? 'No students available.'
                      : 'All students are enrolled.'}
                </li>
              )}
            </ul>
          </div>
          <div className="student-transfer-col">
            <div className="student-transfer-head">
              <strong>In this class ({enrolledStudents.length})</strong>
            </div>
            <ul className="student-transfer-list">
              {enrolledStudents.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    className="student-transfer-item"
                    onClick={() => removeStudent(s.id)}
                  >
                    <span className="muted">← Remove</span>
                    {personLabel(s.user)}
                  </button>
                </li>
              ))}
              {enrolledStudents.length === 0 && (
                <li className="header-sub">No students selected yet.</li>
              )}
            </ul>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="home-btn" disabled={submitting}>
            {submitting ? 'Saving…' : mode === 'create' ? 'Create class' : 'Save changes'}
          </button>
          {mode === 'edit' && detail && (
            <button
              type="button"
              className="home-btn secondary"
              disabled={submitting}
              onClick={handleDelete}
            >
              Delete class
            </button>
          )}
        </div>
      </form>

      {mode === 'edit' && detail && (
        <section className="modal-section">
          <h3>Calendar ({sessions.length} sessions)</h3>
          <div className="form-actions">
            <button type="button" className="home-btn secondary" onClick={handleExportCalendar}>
              Export calendar dates
            </button>
            <label className="home-btn secondary">
              {importingCalendar ? 'Importing…' : 'Import calendar dates'}
              <input
                ref={calendarFileRef}
                type="file"
                accept="application/json,.json"
                onChange={handleImportCalendar}
                disabled={importingCalendar}
                className="sr-only"
              />
            </label>
          </div>
          <div className="inline-form">
            <input
              type="date"
              value={newDate}
              onChange={(e) => {
                setNewDate(e.target.value)
                setCalendarError('')
              }}
            />
            <button type="button" className="home-btn" onClick={handleAddSession}>
              Add date
            </button>
          </div>
          {calendarError && <p className="error">{calendarError}</p>}
          {calendarMessage && <p className="success">{calendarMessage}</p>}
          <p className="header-sub">
            Dates must be unique. Started sessions are locked — their date cannot be changed or
            deleted. Importing leaves existing dates unchanged and does not add duplicates. List is shown oldest → newest.
          </p>
          <ul className="session-list">
            {sessions.map((s) => (
              <li key={s.id}>
                <input
                  type="date"
                  value={s.session_date}
                  disabled={s.is_started}
                  title={s.is_started ? 'Started sessions cannot change date' : undefined}
                  onChange={(e) => handleSessionDateChange(s.id, e.target.value)}
                />
                <span className="muted">
                  {s.is_started ? 'Started (locked)' : 'Not started'}
                </span>
                {!s.is_started && (
                  <button
                    type="button"
                    className="home-btn danger"
                    onClick={() => handleDeleteSession(s.id)}
                  >
                    Delete
                  </button>
                )}
              </li>
            ))}
            {sessions.length === 0 && <li className="header-sub">No session dates yet.</li>}
          </ul>
        </section>
      )}
    </>
  )
}

