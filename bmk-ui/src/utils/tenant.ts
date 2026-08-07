/** App base domain without school subdomain, e.g. localhost or schools.example.com */
const APP_DOMAIN = (import.meta.env.VITE_APP_DOMAIN || 'localhost').toLowerCase()

function currentPortSuffix(): string {
  const { port } = window.location
  return port ? `:${port}` : ''
}

function currentProtocol(): string {
  return window.location.protocol
}

/** Resolve school slug from hostname prefix, e.g. balavikas.localhost → balavikas */
export function getSchoolSlugFromHost(hostname = window.location.hostname): string | null {
  const host = hostname.toLowerCase().split(':')[0]

  if (host === APP_DOMAIN || host === '127.0.0.1') {
    return null
  }

  const suffix = `.${APP_DOMAIN}`
  if (host.endsWith(suffix)) {
    const sub = host.slice(0, -suffix.length)
    if (sub && !sub.includes('.')) return sub
  }

  // Fallback: school.example.com style when APP_DOMAIN is example.com
  const parts = host.split('.')
  if (parts.length >= 3 && parts[0] !== 'www') {
    return parts[0]
  }

  return null
}

export function schoolSiteOrigin(schoolSlug: string): string {
  return `${currentProtocol()}//${schoolSlug}.${APP_DOMAIN}${currentPortSuffix()}`
}

export function platformOrigin(): string {
  return `${currentProtocol()}//${APP_DOMAIN}${currentPortSuffix()}`
}

export function schoolSiteUrl(schoolSlug: string, path = '/'): string {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${schoolSiteOrigin(schoolSlug)}${normalized}`
}
