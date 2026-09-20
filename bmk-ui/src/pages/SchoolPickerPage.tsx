import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchSchoolCatalog } from '../api/public'
import type { SchoolCatalogType, SchoolSummary } from '../types/content'
import { schoolDisplayHost, schoolSiteUrl } from '../utils/tenant'
import { environmentBannerLabel, resolveAppEnvironment } from '../utils/appEnv'

const APP_ENV = resolveAppEnvironment()
const ENV_BANNER = environmentBannerLabel(APP_ENV)

type Language = 'en' | 'te' | 'sa'

const pickerCopy = {
  en: { nav: ['Home', 'About', 'Features', 'Schools', 'Resources', 'Contact'], login: 'Login', started: 'Get started', language: 'Language', lead: 'Find your school by programme — language, music/arts, or academic.', programmes: 'Programmes', choose: 'Choose a programme', chooseLead: 'Language, music/arts, or academic schools.', subjectLead: 'Pick a subject or stream.', schoolLead: 'Open your school site.', loading: 'Loading…', loadError: 'Could not load schools.', subjects: 'subjects', viewSubjects: 'View subjects', other: 'Other schools', noSchools: 'No schools are available yet.', schools: 'schools', viewSchools: 'View schools', noSubjects: 'No subjects in this programme yet.', openSchool: 'Open school', noSchoolsSubject: 'No schools in this subject yet. Check back soon.' },
  te: { nav: ['హోమ్', 'మా గురించి', 'ఫీచర్లు', 'పాఠశాలలు', 'వనరులు', 'సంప్రదించండి'], login: 'లాగిన్', started: 'ప్రారంభించండి', language: 'భాష', lead: 'ప్రోగ్రామ్ ద్వారా మీ పాఠశాలను కనుగొనండి — భాష, సంగీతం/కళలు లేదా విద్యా పాఠశాలలు.', programmes: 'ప్రోగ్రామ్‌లు', choose: 'ఒక ప్రోగ్రామ్ ఎంచుకోండి', chooseLead: 'భాష, సంగీతం/కళలు లేదా విద్యా పాఠశాలలు.', subjectLead: 'ఒక విషయం లేదా విభాగాన్ని ఎంచుకోండి.', schoolLead: 'మీ పాఠశాల సైట్‌ను తెరవండి.', loading: 'లోడ్ అవుతోంది…', loadError: 'పాఠశాలలను లోడ్ చేయలేకపోయాము.', subjects: 'విషయాలు', viewSubjects: 'విషయాలను చూడండి', other: 'ఇతర పాఠశాలలు', noSchools: 'ఇంకా పాఠశాలలు అందుబాటులో లేవు.', schools: 'పాఠశాలలు', viewSchools: 'పాఠశాలలను చూడండి', noSubjects: 'ఈ ప్రోగ్రామ్‌లో ఇంకా విషయాలు లేవు.', openSchool: 'పాఠశాలను తెరవండి', noSchoolsSubject: 'ఈ విషయంలో ఇంకా పాఠశాలలు లేవు. దయచేసి తర్వాత చూడండి.' },
  sa: { nav: ['मुखपृष्ठम्', 'अस्माकम् विषये', 'विशेषताः', 'विद्यालयाः', 'संसाधनानि', 'सम्पर्कः'], login: 'प्रवेशः', started: 'आरभत', language: 'भाषा', lead: 'कार्यक्रमानुसारं भवतः विद्यालयम् अन्विष्यताम् — भाषा, सङ्गीत/कला, अथवा शैक्षणिकम्।', programmes: 'कार्यक्रमाः', choose: 'कार्यक्रमं चिनुत', chooseLead: 'भाषा-, सङ्गीत/कला-, अथवा शैक्षणिक-विद्यालयाः।', subjectLead: 'विषयं वा विभागं चिनुत।', schoolLead: 'भवतः विद्यालय-जालस्थलं उद्घाटयत।', loading: 'लोड् भवति…', loadError: 'विद्यालयान् भारयितुं न शक्यते।', subjects: 'विषयाः', viewSubjects: 'विषयान् पश्यत', other: 'अन्ये विद्यालयाः', noSchools: 'अद्यापि विद्यालयाः न सन्ति।', schools: 'विद्यालयाः', viewSchools: 'विद्यालयान् पश्यत', noSubjects: 'अस्मिन् कार्यक्रमे अद्यापि विषयाः न सन्ति।', openSchool: 'विद्यालयम् उद्घाटयत', noSchoolsSubject: 'अस्मिन् विषये अद्यापि विद्यालयाः न सन्ति। पुनः पश्चात् पश्यत।' },
} as const

const languageNames: Record<Language, string> = { en: 'English', te: 'తెలుగు', sa: 'संस्कृतम्' }

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
  const [searchParams] = useSearchParams()
  const requestedLanguage = searchParams.get('lang') as Language | null
  const [catalog, setCatalog] = useState<SchoolCatalogType[]>([])
  const [uncategorized, setUncategorized] = useState<SchoolSummary[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState<Step>({ level: 'types' })
  const [menuOpen, setMenuOpen] = useState(false)
  const [language, setLanguage] = useState<Language>(() => requestedLanguage && pickerCopy[requestedLanguage] ? requestedLanguage : (localStorage.getItem('bmk-language') as Language) || 'en')
  const t = pickerCopy[language]

  useEffect(() => {
    localStorage.setItem('bmk-language', language)
    document.documentElement.lang = language === 'te' ? 'te' : language === 'sa' ? 'sa' : 'en'
    document.documentElement.dataset.language = language
  }, [language])

  useEffect(() => {
    fetchSchoolCatalog()
      .then((data) => {
        setCatalog(data.catalog || [])
        setUncategorized(
          (data.schools || []).filter((s) => !s.type_slug || !s.subtype_slug),
        )
      })
      .catch(() => setError('load'))
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
      return { title: t.choose, subtitle: t.chooseLead }
    }
    if (step.level === 'subtypes') {
      return { title: step.typeName, subtitle: t.subjectLead }
    }
    return { title: step.subtypeName, subtitle: t.schoolLead }
  }

  const { title, subtitle } = heading()

  return (
    <div className="platform-page picker-page">
      {ENV_BANNER && (
        <div className={`env-banner env-${APP_ENV}`} role="status">
          {ENV_BANNER}
        </div>
      )}

      <header className="platform-header">
        <Link className="platform-header-brand" to="/" onClick={() => setMenuOpen(false)}>
          <img src="/logo.svg" alt="Balamukundam" width={46} height={46} /><span>Balāmukundam</span>
        </Link>
        <button className="platform-menu-toggle" type="button" aria-label={language === 'en' ? 'Toggle navigation menu' : t.nav[0]} aria-expanded={menuOpen} onClick={() => setMenuOpen((open) => !open)}><span /><span /><span /></button>
        <nav className={`platform-nav ${menuOpen ? 'open' : ''}`} aria-label="Platform navigation">
          <Link to={`/?lang=${language}#home`} onClick={() => setMenuOpen(false)}>{t.nav[0]}</Link><Link to={`/?lang=${language}#about`} onClick={() => setMenuOpen(false)}>{t.nav[1]}</Link><Link to={`/?lang=${language}#features`} onClick={() => setMenuOpen(false)}>{t.nav[2]}</Link>
          <Link to={`/schools?lang=${language}`} onClick={() => setMenuOpen(false)}>{t.nav[3]}</Link><Link to={`/?lang=${language}#contact`} onClick={() => setMenuOpen(false)}>{t.nav[5]}</Link>
          <label className="platform-language"><span>{t.language}</span><select value={language} onChange={(event) => setLanguage(event.target.value as Language)} aria-label={t.language}>{(Object.keys(languageNames) as Language[]).map((code) => <option key={code} value={code}>{languageNames[code]}</option>)}</select></label>
        </nav>
      </header>

      <section className="platform-hero picker-hero">
        <img className="platform-hero-logo" src="/logo.svg" alt="" />
        <h1 className="platform-brand-en">Balāmukundam</h1>
        <p className="platform-hero-lead">
          {t.lead}
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
            {t.programmes}
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
            <p>{t.loading}</p>
          </article>
        )}
        {error && <p className="error">{t.loadError}</p>}

        {!loading && !error && step.level === 'types' && (
          <div className="home-card-grid">
            {catalog.map((schoolType) => (
              <article className="home-card picker-nav-card" key={schoolType.slug}>
                <h3>{schoolType.name}</h3>
                <p className="muted">
                  {schoolType.subtypes.length} {t.subjects}
                </p>
                <p>
                  <button
                    type="button"
                    className="home-btn"
                    onClick={() =>
                      setStep({ level: 'subtypes', typeSlug: schoolType.slug, typeName: schoolType.name })
                    }
                  >
                    {t.viewSubjects}
                  </button>
                </p>
              </article>
            ))}
            {uncategorized.length > 0 && (
              <article className="home-card picker-nav-card">
                <h3>{t.other}</h3>
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
              <p>{t.noSchools}</p>
            )}
          </div>
        )}

        {!loading && !error && step.level === 'subtypes' && selectedType && (
          <div className="home-card-grid">
            {selectedType.subtypes.map((st) => (
              <article className="home-card picker-nav-card" key={st.slug}>
                <h3>{st.name}</h3>
                <p className="muted">
                  {st.schools.length} {t.schools}
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
                    {t.viewSchools}
                  </button>
                </p>
              </article>
            ))}
            {selectedType.subtypes.length === 0 && <p>{t.noSubjects}</p>}
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
                    {t.openSchool}
                  </a>
                </p>
              </article>
            ))}
            {(selectedSubtype?.schools || []).length === 0 && (
              <p>{t.noSchoolsSubject}</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
