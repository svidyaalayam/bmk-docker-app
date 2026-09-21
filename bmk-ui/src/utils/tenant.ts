/** App base domain without school subdomain, e.g. localhost or balamukundam.com */
const APP_DOMAIN = (import.meta.env.VITE_APP_DOMAIN || 'localhost').toLowerCase()

function currentPortSuffix(): string {
  const { port } = window.location
  return port ? `:${port}` : ''
}

function currentProtocol(): string {
  return window.location.protocol
}

/**
 * Resolve school host prefix from hostname.
 * Examples: balavikas.localhost → balavikas
 *           uk-telugu.localhost → uk-telugu
 *           uk-telugu.balamukundam.com → uk-telugu (when APP_DOMAIN=balamukundam.com)
 * Legacy dotted prefixes are normalised, e.g. uk.telugu.localhost → uk-telugu.
 */
export function getSchoolSlugFromHost(hostname = window.location.hostname): string | null {
  const host = hostname.toLowerCase().split(':')[0]

  if (host === APP_DOMAIN || host === '127.0.0.1') {
    return null
  }

  const suffix = `.${APP_DOMAIN}`
  if (host.endsWith(suffix)) {
    const sub = host.slice(0, -suffix.length)
    if (sub) return sub.replaceAll('.', '-')
  }

  return null
}

/** Build origin for a school slug/host-prefix. */
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

/** Display hostname for a school (prefer stored domain, else slug.APP_DOMAIN). */
export function schoolDisplayHost(school: { slug: string; domain?: string }): string {
  if (school.domain) return school.domain
  return `${school.slug}.${APP_DOMAIN}`
}
