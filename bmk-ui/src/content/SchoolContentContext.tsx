import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchHomepageContent } from '../api/public'
import type { Course, HomepageContent, SchoolSettings } from '../types/content'

interface SchoolContentValue {
  loading: boolean
  error: string
  schoolSlug: string
  school: SchoolSettings
  courses: Course[]
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
  updated_at: '',
}

const SchoolContentContext = createContext<SchoolContentValue | undefined>(undefined)

export function SchoolContentProvider({
  schoolSlug,
  children,
}: {
  schoolSlug: string
  children: ReactNode
}) {
  const [content, setContent] = useState<HomepageContent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const refresh = async () => {
    if (!schoolSlug) return
    const data = await fetchHomepageContent(schoolSlug)
    setContent(data)
  }

  useEffect(() => {
    if (!schoolSlug) {
      setLoading(false)
      setError('No school selected in the site address.')
      return
    }
    let cancelled = false
    setLoading(true)
    setError('')
    fetchHomepageContent(schoolSlug)
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
  }, [schoolSlug])

  const value = useMemo<SchoolContentValue>(
    () => ({
      loading,
      error,
      schoolSlug,
      school: content?.school ?? { ...fallbackSchool, school_slug: schoolSlug },
      courses: content?.courses ?? [],
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
