import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import axios from 'axios'
import {
  importFirebaseUsers,
  listStudents,
  listTeachers,
  listUsers,
  updateStudent,
  updateTeacher,
} from '../api/school'
import type { UserImportDuplicate, UserImportResult } from '../api/school'
import { activateUser, listPendingUsers } from '../api/auth'
import DataTable, { type DataTableColumn } from '../components/DataTable'
import SiteHeader from '../components/SiteHeader'
import type { User } from '../types/auth'
import type { Gender, StudentProfile, TeacherProfile } from '../types/school'
import { getErrorMessage } from '../utils/errors'

type EditTarget =
  | { kind: 'teacher'; profile: TeacherProfile }
  | { kind: 'student'; profile: StudentProfile }
  | null

type ImportRowError = { row: number; error: string }
type AssignmentFilter = 'all' | 'unassigned' | 'assigned'
type RecentFilter = 'all' | '7' | '30' | '90'
type ExportableProfile = StudentProfile | TeacherProfile

function fullName(first?: string, last?: string): string {
  return `${first || ''} ${last || ''}`.trim()
}

function filterProfiles<T extends ExportableProfile>(profiles: T[], assignment: AssignmentFilter, recent: RecentFilter): T[] {
  const cutoff = recent === 'all' ? null : Date.now() - Number(recent) * 24 * 60 * 60 * 1000
  return profiles.filter((profile) => {
    const assignmentMatches = assignment === 'all' || (assignment === 'unassigned' && profile.class_assignment_count === 0) || (assignment === 'assigned' && profile.class_assignment_count > 0)
    const joined = new Date(profile.user.date_joined).getTime()
    return assignmentMatches && (cutoff === null || (!Number.isNaN(joined) && joined >= cutoff))
  })
}

function downloadSelectedUsers<T extends ExportableProfile>(kind: 'students' | 'teachers', profiles: T[]) {
  const payload = profiles.map((profile) => {
    const user = profile.user
    const isStudent = kind === 'students'
    const student = isStudent ? (profile as StudentProfile) : null
    return {
      uid: user.legacy_uid || `bmk-user-${user.id}`,
      email: user.email || user.username,
      auth: {
        displayName: fullName(user.first_name, user.last_name) || null,
        phoneNumber: user.phone_number || null,
        photoURL: null,
        disabled: user.is_active === false,
        emailVerified: Boolean(user.email_verified),
        creationTime: user.date_joined || '',
        lastSignInTime: user.last_login || null,
      },
      firestore: {
        firestoreDocumentId: user.email || user.username,
        loginid: user.email || user.username,
        gender: profile.gender === 'M' ? (isStudent ? 'Boy' : 'Male') : (isStudent ? 'Girl' : 'Female'),
        contactnumber: profile.phone || user.phone_number || '',
        city: student?.address || '',
        accountsuspended: !profile.is_active || user.is_active === false,
        accepted: Boolean(user.email_verified),
        usertype: isStudent ? 0 : 1,
        admincomments: student?.notes || '',
        dataverifiedby: '',
        parentsname: student?.parent_name || '',
        additionalinfo: '',
        photourl: '',
        dataverifieddate: '',
        teachername: '',
        surname: user.last_name || '',
        dob: student?.date_of_birth || '',
        name: user.first_name || user.username,
        whatsappnumber: student?.parent_phone || '',
      },
    }
  })
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `${kind}-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(url)
}

function csvValue(value: unknown): string {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

function downloadSelectedUsersCsv<T extends ExportableProfile>(kind: 'students' | 'teachers', profiles: T[]) {
  const isStudent = kind === 'students'
  const headers = [
    'id', 'username', 'email', 'first_name', 'last_name', 'role', 'account_phone',
    'gender', 'profile_phone', 'class_assignment_count', 'profile_active', 'account_active',
    'email_verified', 'registration_date', 'last_login', 'legacy_uid',
    ...(isStudent ? ['date_of_birth', 'parent_name', 'parent_phone', 'address', 'notes'] : []),
  ]
  const rows = profiles.map((profile) => {
    const user = profile.user
    const student = isStudent ? (profile as StudentProfile) : null
    return [
      user.id, user.username, user.email, user.first_name, user.last_name,
      isStudent ? 'STUDENT' : 'TEACHER', user.phone_number, profile.gender, profile.phone,
      profile.class_assignment_count, profile.is_active ? 'Yes' : 'No', user.is_active ? 'Yes' : 'No',
      user.email_verified ? 'Yes' : 'No', user.date_joined, user.last_login, user.legacy_uid,
      ...(student ? [student.date_of_birth, student.parent_name, student.parent_phone, student.address, student.notes] : []),
    ]
  })
  const csv = [headers, ...rows].map((row) => row.map(csvValue).join(',')).join('\r\n')
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `${kind}-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function UserExportControls({
  assignment,
  recent,
  selectedCount,
  onAssignmentChange,
  onRecentChange,
  onSelectFiltered,
  onClearSelection,
  onExport,
  onExportCsv,
}: {
  assignment: AssignmentFilter
  recent: RecentFilter
  selectedCount: number
  onAssignmentChange: (value: AssignmentFilter) => void
  onRecentChange: (value: RecentFilter) => void
  onSelectFiltered: () => void
  onClearSelection: () => void
  onExport: () => void
  onExportCsv: () => void
}) {
  return (
    <div className="user-export-controls">
      <label>
        Class assignment
        <select value={assignment} onChange={(event) => onAssignmentChange(event.target.value as AssignmentFilter)}>
          <option value="all">All users</option>
          <option value="unassigned">Not assigned to a class</option>
          <option value="assigned">Assigned to a class</option>
        </select>
      </label>
      <label>
        Registration date
        <select value={recent} onChange={(event) => onRecentChange(event.target.value as RecentFilter)}>
          <option value="all">Any date</option>
          <option value="7">Joined in the last 7 days</option>
          <option value="30">Joined in the last 30 days</option>
          <option value="90">Joined in the last 90 days</option>
        </select>
      </label>
      <div className="form-actions">
        <button type="button" className="tab" onClick={onSelectFiltered}>Select filtered users</button>
        <button type="button" className="tab" onClick={onClearSelection} disabled={selectedCount === 0}>Deselect all</button>
        <button type="button" onClick={onExport} disabled={selectedCount === 0}>
          Export {selectedCount} selected to JSON
        </button>
        <button type="button" className="tab" onClick={onExportCsv} disabled={selectedCount === 0}>
          Export {selectedCount} selected to CSV
        </button>
      </div>
    </div>
  )
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [teachers, setTeachers] = useState<TeacherProfile[]>([])
  const [students, setStudents] = useState<StudentProfile[]>([])
  const [pending, setPending] = useState<User[]>([])
  const [pendingDetails, setPendingDetails] = useState<User | null>(null)
  const [editing, setEditing] = useState<EditTarget>(null)
  const [submitting, setSubmitting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<UserImportResult | null>(null)
  const [importErrors, setImportErrors] = useState<ImportRowError[]>([])
  const [duplicateUsers, setDuplicateUsers] = useState<UserImportDuplicate[]>([])
  const [studentAssignmentFilter, setStudentAssignmentFilter] = useState<AssignmentFilter>('all')
  const [studentRecentFilter, setStudentRecentFilter] = useState<RecentFilter>('all')
  const [teacherAssignmentFilter, setTeacherAssignmentFilter] = useState<AssignmentFilter>('all')
  const [teacherRecentFilter, setTeacherRecentFilter] = useState<RecentFilter>('all')
  const [selectedStudentIds, setSelectedStudentIds] = useState<Set<number>>(new Set())
  const [selectedTeacherIds, setSelectedTeacherIds] = useState<Set<number>>(new Set())
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const importFileRef = useRef<HTMLInputElement>(null)

  const refresh = async () => {
    const [userData, teacherData, studentData, pendingData] = await Promise.all([
      listUsers(),
      listTeachers(),
      listStudents(),
      listPendingUsers(),
    ])
    setUsers(userData)
    setTeachers(teacherData)
    setStudents(studentData)
    setPending(pendingData)
  }

  useEffect(() => {
    refresh().catch(() => setError('Could not load admin user data.'))
  }, [])

  const admins = useMemo(() => users.filter((u) => u.role === 'ADMIN'), [users])
  const filteredStudents = useMemo(() => filterProfiles(students, studentAssignmentFilter, studentRecentFilter), [students, studentAssignmentFilter, studentRecentFilter])
  const filteredTeachers = useMemo(() => filterProfiles(teachers, teacherAssignmentFilter, teacherRecentFilter), [teachers, teacherAssignmentFilter, teacherRecentFilter])
  const blockedStudents = useMemo(() => students.filter((student) => student.account_blocked), [students])
  const selectedStudents = useMemo(() => students.filter((student) => selectedStudentIds.has(student.id)), [students, selectedStudentIds])
  const selectedTeachers = useMemo(() => teachers.filter((teacher) => selectedTeacherIds.has(teacher.id)), [teachers, selectedTeacherIds])

  const handleActivate = useCallback(async (userId: number) => {
    setError('')
    setMessage('')
    try {
      await activateUser(userId)
      setMessage('User activated.')
      await refresh()
      return true
    } catch (err) {
      setError(getErrorMessage(err, 'Could not activate user.'))
      return false
    }
  }, [])

  const handleUnblockStudent = useCallback(async (student: StudentProfile) => {
    setError('')
    setMessage('')
    try {
      await updateStudent(student.id, { account_blocked: false, block_reason: '' })
      setMessage('Student account unblocked.')
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not unblock student account.'))
    }
  }, [])

  const importFile = async (file: File, skipDuplicates = false) => {
    setImporting(true)
    setError('')
    setMessage('')
    setImportResult(null)
    setImportErrors([])
    setDuplicateUsers([])
    try {
      const result = await importFirebaseUsers(file, skipDuplicates)
      setImportResult(result)
      if (importFileRef.current) importFileRef.current.value = ''
      await refresh()
    } catch (err) {
      const payload = axios.isAxiosError(err)
        ? (err.response?.data as { errors?: unknown; duplicates?: unknown } | undefined)
        : undefined
      const details = payload?.errors
      if (Array.isArray(details)) {
        setImportErrors(
          details.filter(
            (detail): detail is ImportRowError =>
              typeof detail === 'object' &&
              detail !== null &&
              typeof (detail as ImportRowError).row === 'number' &&
              typeof (detail as ImportRowError).error === 'string',
          ),
        )
      }
      if (Array.isArray(payload?.duplicates)) {
        setDuplicateUsers(
          payload.duplicates.filter(
            (detail): detail is UserImportDuplicate =>
              typeof detail === 'object' &&
              detail !== null &&
              typeof (detail as UserImportDuplicate).row === 'number' &&
              typeof (detail as UserImportDuplicate).email === 'string' &&
              typeof (detail as UserImportDuplicate).reason === 'string',
          ),
        )
      }
      setError(getErrorMessage(err, 'Could not import the JSON file.'))
    } finally {
      setImporting(false)
    }
  }

  const handleImport = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const file = importFileRef.current?.files?.[0]
    if (!file) {
      setError('Choose a JSON file to import.')
      return
    }
    await importFile(file)
  }

  const handleContinueImport = async () => {
    const file = importFileRef.current?.files?.[0]
    if (!file) {
      setDuplicateUsers([])
      setError('Choose the JSON file again before continuing the import.')
      return
    }
    await importFile(file, true)
  }

  const pendingColumns = useMemo<DataTableColumn<User>[]>(
    () => [
      { key: 'email', header: 'Email', getValue: (u) => u.email },
      {
        key: 'name',
        header: 'Name',
        getValue: (u) => fullName(u.first_name, u.last_name),
      },
      { key: 'role', header: 'Role', getValue: (u) => u.role },
      { key: 'phone', header: 'Phone', getValue: (u) => u.phone_number || '' },
      {
        key: 'registered',
        header: 'Date registered',
        getValue: (u) => new Date(u.date_joined).toLocaleDateString(),
        sortValue: (u) => u.date_joined,
      },
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (u) => (
          <button type="button" className="home-btn" onClick={() => setPendingDetails(u)}>
            Show details
          </button>
        ),
      },
    ],
    [],
  )

  const teacherColumns = useMemo<DataTableColumn<TeacherProfile>[]>(
    () => [
      {
        key: 'name',
        header: 'Name',
        getValue: (t) => fullName(t.user.first_name, t.user.last_name),
      },
      { key: 'email', header: 'Email', getValue: (t) => t.user.email || '' },
      { key: 'gender', header: 'Gender', getValue: (t) => t.gender },
      {
        key: 'phone',
        header: 'Phone',
        getValue: (t) => t.phone || t.user.phone_number || '',
      },
      {
        key: 'active',
        header: 'Active',
        getValue: (t) => (t.is_active && t.user.is_active ? 'Yes' : 'No'),
      },
      { key: 'classes', header: 'Classes', getValue: (t) => t.class_assignment_count },
      {
        key: 'joined',
        header: 'Registered',
        getValue: (t) => new Date(t.user.date_joined).toLocaleDateString(),
        sortValue: (t) => t.user.date_joined,
      },
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (t) => (
          <button
            type="button"
            className="home-btn"
            onClick={() => {
              setMessage('')
              setError('')
              setEditing({ kind: 'teacher', profile: t })
            }}
          >
            Edit
          </button>
        ),
      },
    ],
    [],
  )

  const studentColumns = useMemo<DataTableColumn<StudentProfile>[]>(
    () => [
      {
        key: 'name',
        header: 'Name',
        getValue: (s) => fullName(s.user.first_name, s.user.last_name),
      },
      { key: 'email', header: 'Email', getValue: (s) => s.user.email || '' },
      { key: 'gender', header: 'Gender', getValue: (s) => s.gender },
      { key: 'parent', header: 'Parent', getValue: (s) => s.parent_name || '' },
      {
        key: 'phone',
        header: 'Phone',
        getValue: (s) => s.phone || s.user.phone_number || '',
      },
      {
        key: 'active',
        header: 'Active',
        getValue: (s) => (s.is_active && s.user.is_active ? 'Yes' : 'No'),
      },
      { key: 'classes', header: 'Classes', getValue: (s) => s.class_assignment_count },
      {
        key: 'joined',
        header: 'Registered',
        getValue: (s) => new Date(s.user.date_joined).toLocaleDateString(),
        sortValue: (s) => s.user.date_joined,
      },
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (s) => (
          <button
            type="button"
            className="home-btn"
            onClick={() => {
              setMessage('')
              setError('')
              setEditing({ kind: 'student', profile: s })
            }}
          >
            Edit
          </button>
        ),
      },
    ],
    [],
  )

  const blockedStudentColumns = useMemo<DataTableColumn<StudentProfile>[]>(
    () => [
      {
        key: 'name',
        header: 'Name',
        getValue: (s) => fullName(s.user.first_name, s.user.last_name),
      },
      { key: 'email', header: 'Email', getValue: (s) => s.user.email || '' },
      { key: 'reason', header: 'Reason for blocking', getValue: (s) => s.block_reason || 'Not provided' },
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (s) => (
          <button type="button" className="home-btn secondary" onClick={() => handleUnblockStudent(s)}>
            Unblock
          </button>
        ),
      },
    ],
    [handleUnblockStudent],
  )

  const adminColumns = useMemo<DataTableColumn<User>[]>(
    () => [
      {
        key: 'name',
        header: 'Name',
        getValue: (u) => fullName(u.first_name, u.last_name),
      },
      { key: 'email', header: 'Email', getValue: (u) => u.email || '' },
      { key: 'phone', header: 'Phone', getValue: (u) => u.phone_number || '' },
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
            <h1>User Management</h1>
            <p className="header-sub">
              Review registrations, import legacy users, and edit student or teacher details.
              Passwords are never shown here.
            </p>
          </div>
        </header>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}

        <section className="dash-panel">
          <h2>Import legacy users</h2>
          <p className="header-sub">
            Upload the Firebase JSON export. A usertype of 0 creates a student, 1 creates a
            teacher, and 2 creates an admin. Existing email addresses or Firebase IDs are
            skipped. Imported users must use “Forgot password” to choose a new password before
            signing in.
          </p>
          <form className="admin-form" onSubmit={handleImport}>
            <div className="form-actions">
              <input ref={importFileRef} type="file" accept="application/json,.json" />
              <button type="submit" disabled={importing}>
                {importing ? 'Importing…' : 'Import JSON users'}
              </button>
            </div>
          </form>
          {importResult && (
            <div className="success" role="status">
              <strong>Import completed successfully.</strong>
              <p>
                {importResult.created_count} user{importResult.created_count === 1 ? '' : 's'} created:
                {' '}
                {importResult.created_by_role.STUDENT} students,{' '}
                {importResult.created_by_role.TEACHER} teachers, and{' '}
                {importResult.created_by_role.ADMIN} admins.
              </p>
              <p>
                {importResult.skipped_count} existing user{importResult.skipped_count === 1 ? '' : 's'} skipped.
                {' '}
                {importResult.password_note}
              </p>
            </div>
          )}
          {importErrors.length > 0 && (
            <div className="error" role="alert">
              <strong>The import was not completed. Correct these rows and upload the file again:</strong>
              <ul>
                {importErrors.slice(0, 20).map((detail) => (
                  <li key={detail.row}>
                    Row {detail.row}: {detail.error}
                  </li>
                ))}
              </ul>
              {importErrors.length > 20 && (
                <p>Plus {importErrors.length - 20} more row errors.</p>
              )}
            </div>
          )}
          {duplicateUsers.length > 0 && (
            <div className="error" role="alert">
              <strong>
                {duplicateUsers.length} duplicate user{duplicateUsers.length === 1 ? '' : 's'} found.
                No users have been imported yet.
              </strong>
              <ul>
                {duplicateUsers.slice(0, 20).map((detail) => (
                  <li key={detail.row}>
                    Row {detail.row}: {detail.email} — {detail.reason}
                  </li>
                ))}
              </ul>
              {duplicateUsers.length > 20 && (
                <p>Plus {duplicateUsers.length - 20} more duplicate users.</p>
              )}
              <div className="form-actions">
                <button type="button" onClick={handleContinueImport} disabled={importing}>
                  {importing ? 'Importing…' : 'Continue with remaining users'}
                </button>
                <button
                  type="button"
                  className="tab"
                  disabled={importing}
                  onClick={() => {
                    setDuplicateUsers([])
                    setError('')
                  }}
                >
                  Cancel import
                </button>
              </div>
            </div>
          )}
        </section>

        <section className="dash-panel">
          <h2>Pending activation ({pending.length})</h2>
          <p className="header-sub">
            Email confirmed — waiting for admin approval before they can sign in.
          </p>
          <DataTable
            rows={pending}
            columns={pendingColumns}
            rowKey={(u) => u.id}
            emptyMessage="No users waiting for activation."
            searchPlaceholder="Filter pending users…"
          />
        </section>

        <section className="dash-panel">
          <h2>Teachers ({teachers.length})</h2>
          <UserExportControls
            assignment={teacherAssignmentFilter}
            recent={teacherRecentFilter}
            selectedCount={selectedTeachers.length}
            onAssignmentChange={setTeacherAssignmentFilter}
            onRecentChange={setTeacherRecentFilter}
            onSelectFiltered={() => setSelectedTeacherIds(new Set(filteredTeachers.map((teacher) => teacher.id)))}
            onClearSelection={() => setSelectedTeacherIds(new Set())}
            onExport={() => downloadSelectedUsers('teachers', selectedTeachers)}
            onExportCsv={() => downloadSelectedUsersCsv('teachers', selectedTeachers)}
          />
          <DataTable
            rows={filteredTeachers}
            columns={teacherColumns}
            rowKey={(t) => t.id}
            emptyMessage="No teachers yet."
            searchPlaceholder="Filter teachers…"
            selectedRowKeys={selectedTeacherIds}
            onSelectedRowKeysChange={(keys) => setSelectedTeacherIds(new Set([...keys].map(Number)))}
          />
        </section>

        <section className="dash-panel">
          <h2>Students ({students.length})</h2>
          <UserExportControls
            assignment={studentAssignmentFilter}
            recent={studentRecentFilter}
            selectedCount={selectedStudents.length}
            onAssignmentChange={setStudentAssignmentFilter}
            onRecentChange={setStudentRecentFilter}
            onSelectFiltered={() => setSelectedStudentIds(new Set(filteredStudents.map((student) => student.id)))}
            onClearSelection={() => setSelectedStudentIds(new Set())}
            onExport={() => downloadSelectedUsers('students', selectedStudents)}
            onExportCsv={() => downloadSelectedUsersCsv('students', selectedStudents)}
          />
          <DataTable
            rows={filteredStudents}
            columns={studentColumns}
            rowKey={(s) => s.id}
            emptyMessage="No students yet."
            searchPlaceholder="Filter students…"
            selectedRowKeys={selectedStudentIds}
            onSelectedRowKeysChange={(keys) => setSelectedStudentIds(new Set([...keys].map(Number)))}
          />
        </section>

        <section className="dash-panel">
          <h2>Blocked Students ({blockedStudents.length})</h2>
          <p className="header-sub">
            Students listed here cannot access their classes until unblocked.
          </p>
          <DataTable
            rows={blockedStudents}
            columns={blockedStudentColumns}
            rowKey={(s) => s.id}
            emptyMessage="No students are currently blocked."
            searchPlaceholder="Filter blocked students…"
          />
        </section>

        <section className="dash-panel">
          <h2>Admins ({admins.length})</h2>
          <p className="header-sub">Admin accounts are listed for reference (view only).</p>
          <DataTable
            rows={admins}
            columns={adminColumns}
            rowKey={(u) => u.id}
            emptyMessage="No admins yet."
            searchPlaceholder="Filter admins…"
          />
        </section>

        {pendingDetails && (
          <PendingUserDetailsModal
            user={pendingDetails}
            student={students.find((student) => student.user.id === pendingDetails.id)}
            teacher={teachers.find((teacher) => teacher.user.id === pendingDetails.id)}
            submitting={submitting}
            onClose={() => setPendingDetails(null)}
            onActivate={async () => {
              setSubmitting(true)
              setError('')
              setMessage('')
              try {
                const activated = await handleActivate(pendingDetails.id)
                if (activated) setPendingDetails(null)
              } finally {
                setSubmitting(false)
              }
            }}
          />
        )}

        {editing && (
          <EditUserModal
            target={editing}
            submitting={submitting}
            onClose={() => setEditing(null)}
            onSave={async (payload) => {
              setSubmitting(true)
              setError('')
              setMessage('')
              try {
                if (editing.kind === 'teacher') {
                  await updateTeacher(editing.profile.id, payload)
                  setMessage('Teacher updated.')
                } else {
                  await updateStudent(editing.profile.id, payload)
                  setMessage('Student updated.')
                }
                setEditing(null)
                await refresh()
              } catch (err) {
                setError(getErrorMessage(err, 'Could not save changes.'))
              } finally {
                setSubmitting(false)
              }
            }}
          />
        )}
      </div>
    </div>
  )
}

function PendingUserDetailsModal({
  user,
  student,
  teacher,
  submitting,
  onClose,
  onActivate,
}: {
  user: User
  student?: StudentProfile
  teacher?: TeacherProfile
  submitting: boolean
  onClose: () => void
  onActivate: () => Promise<void>
}) {
  const profile = student || teacher
  const isStudent = Boolean(student)

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="dash-panel edit-user-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pending-user-details-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="pending-user-details-title">User details</h2>
        <p className="header-sub">
          Review this information before deciding whether to activate the account.
        </p>

        <div className="form-grid">
          <label>
            Username
            <input value={user.username} disabled readOnly />
          </label>
          <label>
            Role
            <input value={user.role} disabled readOnly />
          </label>
          <label>
            First name
            <input value={user.first_name || ''} disabled readOnly />
          </label>
          <label>
            Last name
            <input value={user.last_name || ''} disabled readOnly />
          </label>
          <label>
            Email
            <input value={user.email || ''} disabled readOnly />
          </label>
          <label>
            Account phone
            <input value={user.phone_number || ''} disabled readOnly />
          </label>
          <label>
            Email verified
            <input value={user.email_verified ? 'Yes' : 'No'} disabled readOnly />
          </label>
          <label>
            Registered
            <input value={new Date(user.date_joined).toLocaleString()} disabled readOnly />
          </label>
        </div>

        {profile ? (
          <>
            <h3>{isStudent ? 'Student details' : 'Teacher details'}</h3>
            <div className="form-grid">
              <label>
                Gender
                <input value={profile.gender} disabled readOnly />
              </label>
              <label>
                Profile phone
                <input value={profile.phone || ''} disabled readOnly />
              </label>
              {student && (
                <>
                  <label>
                    Date of birth
                    <input value={student.date_of_birth || ''} disabled readOnly />
                  </label>
                  <label>
                    Parent name
                    <input value={student.parent_name || ''} disabled readOnly />
                  </label>
                  <label>
                    Parent phone
                    <input value={student.parent_phone || ''} disabled readOnly />
                  </label>
                  <label className="full">
                    Address
                    <textarea value={student.address || ''} disabled readOnly rows={2} />
                  </label>
                  <label className="full">
                    Notes
                    <textarea value={student.notes || ''} disabled readOnly rows={2} />
                  </label>
                </>
              )}
            </div>
          </>
        ) : (
          <p className="header-sub">No separate student or teacher profile was found for this user.</p>
        )}

        <div className="form-actions">
          <button type="button" className="tab" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button type="button" onClick={onActivate} disabled={submitting || !user.email_verified}>
            {submitting ? 'Activating…' : 'Set active'}
          </button>
        </div>
      </div>
    </div>
  )
}

function EditUserModal({
  target,
  submitting,
  onClose,
  onSave,
}: {
  target: Exclude<EditTarget, null>
  submitting: boolean
  onClose: () => void
  onSave: (payload: Record<string, unknown>) => Promise<void>
}) {
  const profile = target.profile
  const user = profile.user
  const [firstName, setFirstName] = useState(user.first_name || '')
  const [lastName, setLastName] = useState(user.last_name || '')
  const [email, setEmail] = useState(user.email || '')
  const [phoneNumber, setPhoneNumber] = useState(user.phone_number || '')
  const [gender, setGender] = useState<Gender>(profile.gender)
  const [phone, setPhone] = useState(profile.phone || '')
  const [isActive, setIsActive] = useState(Boolean(profile.is_active && user.is_active))
  const [accountBlocked, setAccountBlocked] = useState(
    target.kind === 'student' ? Boolean(target.profile.account_blocked) : false,
  )
  const [blockReason, setBlockReason] = useState(
    target.kind === 'student' ? target.profile.block_reason || '' : '',
  )
  const [dateOfBirth, setDateOfBirth] = useState(
    target.kind === 'student' ? target.profile.date_of_birth || '' : '',
  )
  const [parentName, setParentName] = useState(
    target.kind === 'student' ? target.profile.parent_name || '' : '',
  )
  const [parentPhone, setParentPhone] = useState(
    target.kind === 'student' ? target.profile.parent_phone || '' : '',
  )
  const [address, setAddress] = useState(
    target.kind === 'student' ? target.profile.address || '' : '',
  )
  const [notes, setNotes] = useState(target.kind === 'student' ? target.profile.notes || '' : '')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const payload: Record<string, unknown> = {
      first_name: firstName,
      last_name: lastName,
      email,
      phone_number: phoneNumber || null,
      gender,
      phone,
      is_active: isActive,
    }
    if (target.kind === 'student') {
      payload.date_of_birth = dateOfBirth || null
      payload.parent_name = parentName
      payload.parent_phone = parentPhone
      payload.address = address
      payload.notes = notes
      payload.account_blocked = accountBlocked
      payload.block_reason = accountBlocked ? blockReason : ''
    }
    await onSave(payload)
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="dash-panel edit-user-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-user-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="edit-user-title">
          Edit {target.kind === 'teacher' ? 'teacher' : 'student'}: {user.username}
        </h2>
        <p className="header-sub">Password is not visible and cannot be changed here.</p>

        <form className="admin-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Username
              <input value={user.username} disabled readOnly />
            </label>
            <label>
              Active
              <select
                value={isActive ? 'yes' : 'no'}
                onChange={(e) => setIsActive(e.target.value === 'yes')}
              >
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </label>
            <label>
              First name
              <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
            </label>
            <label>
              Last name
              <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
            </label>
            <label>
              Email
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label>
              Account phone
              <input value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
            </label>
            <label>
              Gender
              <select value={gender} onChange={(e) => setGender(e.target.value as Gender)}>
                <option value="M">{target.kind === 'student' ? 'Boy' : 'Male'}</option>
                <option value="F">{target.kind === 'student' ? 'Girl' : 'Female'}</option>
              </select>
            </label>
            <label>
              Profile phone
              <input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </label>
          </div>

          {target.kind === 'student' && (
            <div className="form-grid">
              <label>
                Date of birth
                <input
                  type="date"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                />
              </label>
              <label>
                Parent name
                <input value={parentName} onChange={(e) => setParentName(e.target.value)} />
              </label>
              <label>
                Parent phone
                <input value={parentPhone} onChange={(e) => setParentPhone(e.target.value)} />
              </label>
              <label className="full">
                Address
                <textarea value={address} onChange={(e) => setAddress(e.target.value)} rows={2} />
              </label>
              <label className="full">
                Notes
                <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
              </label>
              <label>
                Account blocked
                <select
                  value={accountBlocked ? 'yes' : 'no'}
                  onChange={(e) => setAccountBlocked(e.target.value === 'yes')}
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </label>
              <label className="full">
                Reason for blocking
                <textarea
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  rows={2}
                  disabled={!accountBlocked}
                  placeholder="Explain why this student account is blocked"
                />
              </label>
            </div>
          )}

          <div className="form-actions">
            <button type="button" className="tab" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
