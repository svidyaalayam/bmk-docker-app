/** Deployed environment label for UI banners (test / staging / production). */
export type AppEnvironment = 'local' | 'test' | 'staging' | 'production'

export function resolveAppEnvironment(
  explicit = import.meta.env.VITE_APP_ENV,
  domain = import.meta.env.VITE_APP_DOMAIN || 'localhost',
): AppEnvironment {
  const raw = (explicit || '').trim().toLowerCase()
  if (raw === 'test' || raw === 'staging' || raw === 'production' || raw === 'local') {
    return raw
  }

  const host = domain.toLowerCase()
  if (host.startsWith('test.') || host.includes('.test.')) return 'test'
  if (host.startsWith('staging.') || host.includes('.staging.')) return 'staging'
  if (host === 'localhost' || host.endsWith('.localhost')) return 'local'
  return 'production'
}

export function environmentBannerLabel(env: AppEnvironment): string | null {
  switch (env) {
    case 'test':
      return 'TEST ENVIRONMENT'
    case 'staging':
      return 'STAGING ENVIRONMENT'
    case 'local':
      return 'LOCAL DEVELOPMENT'
    default:
      return null
  }
}
