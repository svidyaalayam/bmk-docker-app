import type { LessonApp } from '../types/auth'

/** Base URL for the school's configured lesson application. */
export function lessonAppOrigin(app: LessonApp): string {
  const raw =
    app === 'sunaadam'
      ? (import.meta.env.VITE_SUNAADAM_URL || 'http://localhost:8280').trim()
      : (import.meta.env.VITE_SIKSHAVAHINI_URL || 'http://localhost:8180').trim()
  return raw.replace(/\/$/, '')
}

/**
 * Open the configured lesson app with a BMK access token in the URL hash
 * (hash is not sent to servers in HTTP request logs).
 */
export function openLessonApp(
  app: LessonApp,
  accessToken: string,
  returnTo?: string,
): void {
  const token = accessToken.trim()
  if (!token) return

  const params = new URLSearchParams()
  params.set('bmk_token', token)
  const ret = (returnTo || `${window.location.origin}${window.location.pathname}`).trim()
  if (ret) params.set('return_to', ret)

  window.location.assign(`${lessonAppOrigin(app)}/sso#${params.toString()}`)
}
