import { api } from './client'
import type {
  HomepageContent,
  SchoolCatalogResponse,
  SchoolSettings,
  SchoolSummary,
} from '../types/content'

export async function fetchSchoolCatalog(): Promise<SchoolCatalogResponse> {
  const { data } = await api.get<SchoolCatalogResponse | SchoolSummary[]>('/api/public/schools/')
  // Backward compatible if an older API still returns a flat array.
  if (Array.isArray(data)) {
    return { schools: data, catalog: [] }
  }
  return data
}

/** @deprecated Prefer fetchSchoolCatalog — kept for callers that need a flat list. */
export async function fetchSchools(): Promise<SchoolSummary[]> {
  const data = await fetchSchoolCatalog()
  return data.schools
}

export async function fetchHomepageContent(schoolSlug: string): Promise<HomepageContent> {
  const { data } = await api.get<HomepageContent>('/api/public/homepage/', {
    params: { school: schoolSlug },
  })
  return data
}

export async function fetchSchoolSettings(schoolSlug: string): Promise<SchoolSettings> {
  const { data } = await api.get<SchoolSettings>('/api/public/school/', {
    params: { school: schoolSlug },
  })
  return data
}
