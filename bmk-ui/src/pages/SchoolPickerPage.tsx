import { useEffect, useMemo, useState } from 'react'
import { fetchSchoolCatalog } from '../api/public'
import type { SchoolCatalogType, SchoolSummary } from '../types/content'
import { schoolDisplayHost, schoolSiteUrl } from '../utils/tenant'
import { environmentBannerLabel, resolveAppEnvironment } from '../utils/appEnv'

const APP_ENV = resolveAppEnvironment()
const ENV_BANNER = environmentBannerLabel(APP_ENV)

type Step =
  | { level: 'types' }
  | { level: 'subtypes'; typeSlug: string; typeName: string }
  | {
      level: 'schools'
      typeSlug: string
      typeName: string
      subtypeSlug: string
      subtypeName: string
    }

export default function SchoolPickerPage() {
  const [catalog, setCatalog] = useState<SchoolCatalogType[]>([])
  const [uncategorized, setUncategorized] = useState<SchoolSummary[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState<Step>({ level: 'types' })

  useEffect(() => {
    fetchSchoolCatalog()
      .then((data) => {
        setCatalog(data.catalog || [])
        setUncategorized(
          (data.schools || []).filter((s) => !s.type_slug || !s.subtype_slug),
        )
      })
      .catch(() => setError('Could not load schools.'))
      .finally(() => setLoading(false))
  }, [])

  const selectedType = useMemo(
    () => (step.level === 'types' ? null : catalog.find((t) => t.slug === step.typeSlug) || null),
    [catalog, step],
  )

  const selectedSubtype = useMemo(() => {
    if (step.level !== 'schools' || !selectedType) return null
    return selectedType.subtypes.find((s) => s.slug === step.subtypeSlug) || null
  }, [selectedType, step])

  function heading() {
    if (step.level === 'types') {
      return { title: 'Choose a programme', subtitle: 'Language, music/arts, or academic schools.' }
    }
    if (step.level === 'subtypes') {
      return { title: step.typeName, subtitle: 'Pick a subject or stream.' }
    }
    return { title: step.subtypeName, subtitle: 'Open your school site.' }
  }

  const { title, subtitle } = heading()

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
          <span className="site-brand-text">Balamukundam</span>
        </div>
      </header>

      <section className="platform-hero">
        <img className="platform-hero-logo" src="/logo.svg" alt="" />
        <h1 className="platform-brand-en">Balamukundam</h1>
        <p className="platform-hero-lead">
          Find your school by programme — language, music/arts, or academic.
        </p>
      </section>

      <main className="home-section first">
        <nav className="picker-breadcrumb" aria-label="School picker">
          <button
            type="button"
            className="picker-crumb"
            onClick={() => setStep({ level: 'types' })}
            disabled={step.level === 'types'}
          >
            Programmes
          </button>
          {step.level !== 'types' && (
            <>
              <span className="picker-crumb-sep" aria-hidden="true">
                /
              </span>
              <button
                type="button"
                className="picker-crumb"
                onClick={() =>
                  setStep({
                    level: 'subtypes',
                    typeSlug: step.typeSlug,
                    typeName: step.typeName,
                  })
                }
                disabled={step.level === 'subtypes'}
              >
                {step.typeName}
              </button>
            </>
          )}
          {step.level === 'schools' && (
            <>
              <span className="picker-crumb-sep" aria-hidden="true">
                /
              </span>
              <span className="picker-crumb current">{step.subtypeName}</span>
            </>
          )}
        </nav>

        <div className="home-section-head">
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>

        {loading && (
          <article className="home-panel">
            <p>Loading…</p>
          </article>
        )}
        {error && <p className="error">{error}</p>}

        {!loading && !error && step.level === 'types' && (
          <div className="home-card-grid">
            {catalog.map((t) => (
              <article className="home-card picker-nav-card" key={t.slug}>
                <h3>{t.name}</h3>
                <p className="muted">
                  {t.subtypes.length} subject{t.subtypes.length === 1 ? '' : 's'}
                </p>
                <p>
                  <button
                    type="button"
                    className="home-btn"
                    onClick={() =>
                      setStep({ level: 'subtypes', typeSlug: t.slug, typeName: t.name })
                    }
                  >
                    View subjects
                  </button>
                </p>
              </article>
            ))}
            {uncategorized.length > 0 && (
              <article className="home-card picker-nav-card">
                <h3>Other schools</h3>
                <ul className="picker-school-list">
                  {uncategorized.map((school) => (
                    <li key={school.id}>
                      <a href={schoolSiteUrl(school.slug, '/')}>{school.name}</a>
                    </li>
                  ))}
                </ul>
              </article>
            )}
            {catalog.length === 0 && uncategorized.length === 0 && (
              <p>No schools are available yet.</p>
            )}
          </div>
        )}

        {!loading && !error && step.level === 'subtypes' && selectedType && (
          <div className="home-card-grid">
            {selectedType.subtypes.map((st) => (
              <article className="home-card picker-nav-card" key={st.slug}>
                <h3>{st.name}</h3>
                <p className="muted">
                  {st.schools.length} school{st.schools.length === 1 ? '' : 's'}
                </p>
                <p>
                  <button
                    type="button"
                    className="home-btn"
                    onClick={() =>
                      setStep({
                        level: 'schools',
                        typeSlug: step.typeSlug,
                        typeName: step.typeName,
                        subtypeSlug: st.slug,
                        subtypeName: st.name,
                      })
                    }
                  >
                    View schools
                  </button>
                </p>
              </article>
            ))}
            {selectedType.subtypes.length === 0 && <p>No subjects in this programme yet.</p>}
          </div>
        )}

        {!loading && !error && step.level === 'schools' && (
          <div className="home-card-grid">
            {(selectedSubtype?.schools || []).map((school) => (
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
                  <code>{schoolDisplayHost(school)}</code>
                </p>
                <p>
                  <a className="home-btn" href={schoolSiteUrl(school.slug, '/')}>
                    Open school
                  </a>
                </p>
              </article>
            ))}
            {(selectedSubtype?.schools || []).length === 0 && (
              <p>No schools in this subject yet. Check back soon.</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
