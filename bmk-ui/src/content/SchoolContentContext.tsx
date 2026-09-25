import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchHomepageContent } from '../api/public'
import type { Course, HomepageContent, SchoolSettings } from '../types/content'

interface SchoolContentValue {
  loading: boolean
  error: string
  schoolSlug: string
  school: SchoolSettings
  courses: Course[]
  birthdays: HomepageContent['birthdays']
  refresh: () => Promise<void>
}

const fallbackSchool: SchoolSettings = {
  school_id: 0,
  school_slug: '',
  school_name: 'Online School',
  logo_url: null,
  tagline: '',
  introduction: '',
  secondary_language: '',
  introduction_secondary: '',
  footer_text: '',
  terms_and_conditions: '',
  updated_at: '',
}

const SchoolContentContext = createContext<SchoolContentValue | undefined>(undefined)

export function SchoolContentProvider({ children }: { children: ReactNode }) {
  const [content, setContent] = useState<HomepageContent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const refresh = async () => {
    const data = await fetchHomepageContent()
    setContent(data)
  }

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    fetchHomepageContent()
      .then((data) => {
        if (!cancelled) setContent(data)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        const detail =
          typeof err === 'object' &&
          err !== null &&
          'response' in err &&
          typeof (err as { response?: { data?: { detail?: unknown } } }).response?.data
            ?.detail === 'string'
            ? (err as { response: { data: { detail: string } } }).response.data.detail
            : null
        setError(detail || 'Could not load school homepage content.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const schoolSlug = content?.school.school_slug ?? ''
  const value = useMemo<SchoolContentValue>(
    () => ({
      loading,
      error,
      schoolSlug,
      school: content?.school ?? fallbackSchool,
      courses: content?.courses ?? [],
      birthdays: content?.birthdays ?? [],
      refresh,
    }),
    [loading, error, schoolSlug, content],
  )

  return (
    <SchoolContentContext.Provider value={value}>{children}</SchoolContentContext.Provider>
  )
}

export function useSchoolContent() {
  const ctx = useContext(SchoolContentContext)
  if (!ctx) {
    throw new Error('useSchoolContent must be used within SchoolContentProvider')
  }
  return ctx
}
