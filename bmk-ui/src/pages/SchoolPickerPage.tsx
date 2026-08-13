import { useEffect, useState } from 'react'
import { fetchSchools } from '../api/public'
import type { SchoolSummary } from '../types/content'
import { schoolSiteUrl } from '../utils/tenant'
import { environmentBannerLabel, resolveAppEnvironment } from '../utils/appEnv'

const APP_DOMAIN = (import.meta.env.VITE_APP_DOMAIN || 'localhost').toLowerCase()
const APP_ENV = resolveAppEnvironment()
const ENV_BANNER = environmentBannerLabel(APP_ENV)

const BRAND = {
  english: 'Balamukundam - Vidyalayam',
  devanagari: 'बालमुकुन्दम् - विद्यालयम्',
  telugu: 'బాలముకుందం - విద్యాలయం',
}

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
      {ENV_BANNER && (
        <div className={`env-banner env-${APP_ENV}`} role="status">
          {ENV_BANNER}
        </div>
      )}

      <header className="site-header">
        <div className="site-brand">
          <img className="site-brand-logo" src="/logo.svg" alt="" width={36} height={36} />
          <span className="site-brand-text">{BRAND.english}</span>
        </div>
      </header>

      <section className="platform-hero">
        <img className="platform-hero-logo" src="/logo.svg" alt="" />
        <h1 className="platform-brand-en">{BRAND.english}</h1>
        <p className="platform-brand-hi" lang="hi">
          {BRAND.devanagari}
        </p>
        <p className="platform-brand-te" lang="te">
          {BRAND.telugu}
        </p>
        <p className="platform-hero-lead">Pick your school below. Then tap the button to open it.</p>
      </section>

      <main className="home-section first">
        <div className="home-section-head">
          <h2>Which school are you in?</h2>
          <p>Find your school name and open it.</p>
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
              <div className="school-card-brand">
                {school.logo_url ? (
                  <img
                    className="school-card-logo"
                    src={school.logo_url}
                    alt={`${school.name} logo`}
                    width={48}
                    height={48}
                  />
                ) : (
                  <span className="site-brand-mark" aria-hidden="true">
                    {school.name.slice(0, 2).toUpperCase()}
                  </span>
                )}
                <h3>{school.name}</h3>
              </div>
              <p>
                <code>
                  {school.slug}.{APP_DOMAIN}
                </code>
              </p>
              <p>
                <a className="home-btn" href={schoolSiteUrl(school.slug, '/')}>
                  Open my school
                </a>
              </p>
            </article>
          ))}
        </div>
      </main>
    </div>
  )
}
