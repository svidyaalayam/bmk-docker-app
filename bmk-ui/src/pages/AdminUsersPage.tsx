import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { listStudents, listTeachers, listUsers, updateStudent, updateTeacher } from '../api/school'
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

function fullName(first?: string, last?: string): string {
  return `${first || ''} ${last || ''}`.trim()
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [teachers, setTeachers] = useState<TeacherProfile[]>([])
  const [students, setStudents] = useState<StudentProfile[]>([])
  const [pending, setPending] = useState<User[]>([])
  const [editing, setEditing] = useState<EditTarget>(null)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

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

  const handleActivate = useCallback(async (userId: number) => {
    setError('')
    setMessage('')
    try {
      await activateUser(userId)
      setMessage('User activated.')
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not activate user.'))
    }
  }, [])

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
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (u) => (
          <button type="button" className="home-btn" onClick={() => handleActivate(u.id)}>
            Set Active
          </button>
        ),
      },
    ],
    [handleActivate],
  )

  const teacherColumns = useMemo<DataTableColumn<TeacherProfile>[]>(
    () => [
      { key: 'username', header: 'Username', getValue: (t) => t.user.username },
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
      { key: 'username', header: 'Username', getValue: (s) => s.user.username },
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

  const adminColumns = useMemo<DataTableColumn<User>[]>(
    () => [
      { key: 'username', header: 'Username', getValue: (u) => u.username },
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
              Review registrations and edit student or teacher details. Users are created only
              through registration — passwords are never shown here.
            </p>
          </div>
        </header>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}

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
          <DataTable
            rows={teachers}
            columns={teacherColumns}
            rowKey={(t) => t.id}
            emptyMessage="No teachers yet."
            searchPlaceholder="Filter teachers…"
          />
        </section>

        <section className="dash-panel">
          <h2>Students ({students.length})</h2>
          <DataTable
            rows={students}
            columns={studentColumns}
            rowKey={(s) => s.id}
            emptyMessage="No students yet."
            searchPlaceholder="Filter students…"
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
