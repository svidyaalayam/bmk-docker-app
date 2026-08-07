import type { User } from '../types/auth'

export function getDisplayName(user: User): string {
  const fullName = `${user.first_name} ${user.last_name}`.trim()
  return fullName || user.username
}

export function getInitials(user: User): string {
  const first = user.first_name?.trim()?.[0]
  const last = user.last_name?.trim()?.[0]
  if (first && last) return `${first}${last}`.toUpperCase()
  if (first) return first.toUpperCase()
  return user.username.slice(0, 2).toUpperCase()
}
