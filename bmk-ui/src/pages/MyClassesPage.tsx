import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listClasses } from '../api/classes'
import { useAuth } from '../auth/AuthContext'
import DataTable, { type DataTableColumn } from '../components/DataTable'
import SiteHeader from '../components/SiteHeader'
import type { TeachingClassListItem } from '../types/classes'
import { getErrorMessage } from '../utils/errors'
import { classDetailPath, dashboardPathForRole } from '../utils/routes'

function personLabel(p: { first_name: string; last_name: string; username: string; email?: string }): string {
  const name = `${p.first_name || ''} ${p.last_name || ''}`.trim()
  const email = p.email || 'No email available'
  return name ? `${name} (${email})` : email
}

export default function MyClassesPage() {
  const { user } = useAuth()
  const [classes, setClasses] = useState<TeachingClassListItem[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    listClasses()
      .then(setClasses)
      .catch((err) => setError(getErrorMessage(err, 'Could not load classes.')))
  }, [])

  const columns = useMemo<DataTableColumn<TeachingClassListItem>[]>(
    () => [
      { key: 'name', header: 'Class', getValue: (c) => c.name },
      {
        key: 'teachers',
        header: 'Teachers',
        getValue: (c) => {
          const t1 = personLabel(c.teacher_1)
          const t2 = c.teacher_2 ? personLabel(c.teacher_2) : null
          return t2 ? `${t1}; ${t2}` : t1
        },
      },
      {
        key: 'sessions',
        header: 'Sessions',
        getValue: (c) => String(c.session_count),
      },
      ...(user?.role === 'TEACHER'
        ? [
            {
              key: 'students',
              header: 'Students',
              getValue: (c: TeachingClassListItem) => String(c.student_count),
            } as DataTableColumn<TeachingClassListItem>,
          ]
        : []),
      {
        key: 'actions',
        header: '',
        sortable: false,
        filterable: false,
        render: (c) => (
          <Link className="home-btn" to={classDetailPath(user!.role, c.id)}>
            Open
          </Link>
        ),
      },
    ],
    [user],
  )

  if (!user) return null

  return (
    <div className="page-shell">
      <SiteHeader />
      <div className="dash-shell wide">
        <header className="dash-header compact">
          <div>
            <p className="brand light">My classes</p>
            <h1>{user.role === 'TEACHER' ? 'Assigned classes' : 'Your classes'}</h1>
            <p className="header-sub">
              {user.role === 'TEACHER'
                ? 'Open a class to edit description, calendar, attendance, and homework feedback.'
                : 'Open a class to view the calendar, your comments, and homework.'}
            </p>
            <p className="admin-cta">
              <Link to={dashboardPathForRole(user.role)}>← Dashboard</Link>
            </p>
          </div>
        </header>

        {error && <p className="error">{error}</p>}

        <section className="dash-panel">
          <DataTable
            rows={classes}
            columns={columns}
            rowKey={(c) => c.id}
            emptyMessage="No classes assigned yet."
            searchPlaceholder="Filter classes…"
          />
        </section>
      </div>
    </div>
  )
}
