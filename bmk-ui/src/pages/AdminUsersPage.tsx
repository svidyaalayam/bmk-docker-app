import { useEffect, useMemo, useState, type FormEvent } from 'react'
import {
  createAdmin,
  createStudent,
  createTeacher,
  listStudents,
  listTeachers,
  listUsers,
} from '../api/school'
import SiteHeader from '../components/SiteHeader'
import type { User } from '../types/auth'
import type {
  CreateRole,
  Gender,
  StudentProfile,
  TeacherProfile,
} from '../types/school'
import { getErrorMessage } from '../utils/errors'

const emptyCommon = {
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
}

export default function AdminUsersPage() {
  const [role, setRole] = useState<CreateRole>('STUDENT')
  const [common, setCommon] = useState(emptyCommon)
  const [gender, setGender] = useState<Gender>('M')
  const [phone, setPhone] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [parentName, setParentName] = useState('')
  const [parentPhone, setParentPhone] = useState('')
  const [address, setAddress] = useState('')
  const [notes, setNotes] = useState('')

  const [users, setUsers] = useState<User[]>([])
  const [teachers, setTeachers] = useState<TeacherProfile[]>([])
  const [students, setStudents] = useState<StudentProfile[]>([])

  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const refresh = async () => {
    const [userData, teacherData, studentData] = await Promise.all([
      listUsers(),
      listTeachers(),
      listStudents(),
    ])
    setUsers(userData)
    setTeachers(teacherData)
    setStudents(studentData)
  }

  useEffect(() => {
    refresh().catch(() => setError('Could not load admin user data.'))
  }, [])

  const admins = useMemo(() => users.filter((u) => u.role === 'ADMIN'), [users])

  const resetForm = () => {
    setCommon(emptyCommon)
    setGender('M')
    setPhone('')
    setDateOfBirth('')
    setParentName('')
    setParentPhone('')
    setAddress('')
    setNotes('')
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')
    try {
      if (role === 'ADMIN') {
        const user = await createAdmin(common)
        setMessage(`Admin ${user.username} created.`)
      } else if (role === 'TEACHER') {
        const teacher = await createTeacher({
          ...common,
          gender,
          phone: phone || common.phone_number,
        })
        setMessage(`Teacher ${teacher.user.username} created.`)
      } else {
        const student = await createStudent({
          ...common,
          gender,
          date_of_birth: dateOfBirth || null,
          phone: phone || common.phone_number,
          parent_name: parentName,
          parent_phone: parentPhone,
          address,
          notes,
        })
        setMessage(`Student ${student.user.username} created.`)
      }
      resetForm()
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'Could not create user.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-shell">
      <SiteHeader />

      <div className="dash-shell wide">
        <header className="dash-header compact">
          <div>
            <p className="brand light">Administration</p>
            <h1>User Management</h1>
            <p className="header-sub">Create admins, teachers, and students.</p>
          </div>
        </header>

        <section className="dash-panel">
        <h2>Create user</h2>
        <div className="role-tabs">
          {(['STUDENT', 'TEACHER', 'ADMIN'] as CreateRole[]).map((item) => (
            <button
              key={item}
              type="button"
              className={role === item ? 'tab active' : 'tab'}
              onClick={() => setRole(item)}
            >
              {item}
            </button>
          ))}
        </div>

        <form className="admin-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Username
              <input
                required
                value={common.username}
                onChange={(e) => setCommon({ ...common, username: e.target.value })}
              />
            </label>
            <label>
              Password
              <input
                required
                type="password"
                minLength={8}
                value={common.password}
                onChange={(e) => setCommon({ ...common, password: e.target.value })}
              />
            </label>
            <label>
              First name
              <input
                value={common.first_name}
                onChange={(e) => setCommon({ ...common, first_name: e.target.value })}
              />
            </label>
            <label>
              Last name
              <input
                value={common.last_name}
                onChange={(e) => setCommon({ ...common, last_name: e.target.value })}
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={common.email}
                onChange={(e) => setCommon({ ...common, email: e.target.value })}
              />
            </label>
            <label>
              Account phone
              <input
                value={common.phone_number}
                onChange={(e) => setCommon({ ...common, phone_number: e.target.value })}
              />
            </label>
          </div>

          {(role === 'TEACHER' || role === 'STUDENT') && (
            <div className="form-grid">
              <label>
                Gender
                <select value={gender} onChange={(e) => setGender(e.target.value as Gender)}>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="O">Other</option>
                </select>
              </label>
              <label>
                Profile phone
                <input value={phone} onChange={(e) => setPhone(e.target.value)} />
              </label>
            </div>
          )}

          {role === 'STUDENT' && (
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

          <button type="submit" disabled={submitting}>
            {submitting ? 'Creating…' : `Create ${role.toLowerCase()}`}
          </button>
        </form>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <section className="dash-panel">
        <h2>Admins ({admins.length})</h2>
        <UserTable users={admins} />
      </section>

      <section className="dash-panel">
        <h2>Teachers ({teachers.length})</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Gender</th>
                <th>Phone</th>
              </tr>
            </thead>
            <tbody>
              {teachers.map((teacher) => (
                <tr key={teacher.id}>
                  <td>{teacher.user.username}</td>
                  <td>
                    {teacher.user.first_name} {teacher.user.last_name}
                  </td>
                  <td>{teacher.gender}</td>
                  <td>{teacher.phone || '—'}</td>
                </tr>
              ))}
              {teachers.length === 0 && (
                <tr>
                  <td colSpan={4}>No teachers yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="dash-panel">
        <h2>Students ({students.length})</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Gender</th>
                <th>Parent</th>
                <th>Phone</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>{student.user.username}</td>
                  <td>
                    {student.user.first_name} {student.user.last_name}
                  </td>
                  <td>{student.gender}</td>
                  <td>{student.parent_name || '—'}</td>
                  <td>{student.phone || '—'}</td>
                </tr>
              ))}
              {students.length === 0 && (
                <tr>
                  <td colSpan={5}>No students yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
      </div>
    </div>
  )
}

function UserTable({ users }: { users: User[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>
                {user.first_name} {user.last_name}
              </td>
              <td>{user.email || '—'}</td>
              <td>{user.phone_number || '—'}</td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr>
              <td colSpan={4}>No admins yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
