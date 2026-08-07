import { api } from './client'
import type { HomepageContent, SchoolSettings, SchoolSummary } from '../types/content'

export async function fetchSchools(): Promise<SchoolSummary[]> {
  const { data } = await api.get<SchoolSummary[]>('/api/public/schools/')
  return data
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
