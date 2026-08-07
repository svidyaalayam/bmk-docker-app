import axios from 'axios'

export function getErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback
  const data = error.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data === 'object') {
    const record = data as Record<string, unknown>
    if (typeof record.detail === 'string') return record.detail
    const firstKey = Object.keys(record)[0]
    const value = firstKey ? record[firstKey] : null
    if (typeof value === 'string') return `${firstKey}: ${value}`
    if (Array.isArray(value) && typeof value[0] === 'string') {
      return `${firstKey}: ${value[0]}`
    }
  }
  return fallback
}
