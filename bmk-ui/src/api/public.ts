import { api } from './client'
import type { HomepageContent, SchoolSettings } from '../types/content'

export async function fetchHomepageContent(): Promise<HomepageContent> {
  const { data } = await api.get<HomepageContent>('/api/public/homepage/')
  return data
}

export async function fetchSchoolSettings(): Promise<SchoolSettings> {
  const { data } = await api.get<SchoolSettings>('/api/public/school/')
  return data
}
