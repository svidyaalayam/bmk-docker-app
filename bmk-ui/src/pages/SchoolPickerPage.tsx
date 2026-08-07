import { useEffect, useState } from 'react'
import { fetchSchools } from '../api/public'
import type { SchoolSummary } from '../types/content'
import { schoolSiteUrl } from '../utils/tenant'

export default function SchoolPickerPage() {
  const [schools, setSchools] = useState<SchoolSummary[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSchools()
      .then(setSchools)
      .catch(() => setError('Could not load schools.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page-shell">
      <header className="site-header">
        <div className="site-brand">
          <span className="site-brand-mark">BMK</span>
          <span className="site-brand-text">Online School Platform</span>
        </div>
      </header>

      <main className="home-section first">
        <div className="home-section-head">
          <h2>Choose your school</h2>
          <p>Each school has its own site address — school name first, then the shared platform.</p>
        </div>

        {loading && (
          <article className="home-panel">
            <p>Loading schools…</p>
          </article>
        )}
        {error && <p className="error">{error}</p>}

        <div className="home-card-grid">
          {schools.map((school) => (
            <article className="home-card" key={school.id}>
              <h3>{school.name}</h3>
              <p>
                <code>{school.slug}.localhost</code>
              </p>
              <p>
                <a className="home-btn" href={schoolSiteUrl(school.slug, '/')}>
                  Open school site
                </a>
              </p>
            </article>
          ))}
        </div>
      </main>
    </div>
  )
}
