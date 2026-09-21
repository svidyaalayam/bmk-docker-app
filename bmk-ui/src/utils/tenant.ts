/** App base domain without school subdomain, e.g. localhost or balamukundam.com */
const APP_DOMAIN = (import.meta.env.VITE_APP_DOMAIN || 'localhost').toLowerCase()
const TENANT_HOST_SUFFIX = (import.meta.env.VITE_TENANT_HOST_SUFFIX || '').toLowerCase()
const PLATFORM_HOSTNAME = (import.meta.env.VITE_PLATFORM_HOSTNAME || APP_DOMAIN).toLowerCase()

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
 *           uk-telugu-test.balamukundam.com → uk-telugu
 * Legacy dotted prefixes are normalised, e.g. uk.telugu.localhost → uk-telugu.
 */
export function getSchoolSlugFromHost(hostname = window.location.hostname): string | null {
  const host = hostname.toLowerCase().split(':')[0]

  if (host === PLATFORM_HOSTNAME || host === '127.0.0.1') {
    return null
  }

  const suffix = `.${APP_DOMAIN}`
  if (host.endsWith(suffix)) {
    const sub = host.slice(0, -suffix.length)
    if (sub) {
      const slug = sub.replaceAll('.', '-')
      if (TENANT_HOST_SUFFIX && !slug.endsWith(TENANT_HOST_SUFFIX)) return null
      return TENANT_HOST_SUFFIX ? slug.slice(0, -TENANT_HOST_SUFFIX.length) : slug
    }
  }

  return null
}

/** Build origin for a school slug/host-prefix. */
export function schoolSiteOrigin(schoolSlug: string): string {
  const dnsLabel = schoolSlug.replaceAll('.', '-')
  return `${currentProtocol()}//${dnsLabel}${TENANT_HOST_SUFFIX}.${APP_DOMAIN}${currentPortSuffix()}`
}

export function platformOrigin(): string {
  return `${currentProtocol()}//${PLATFORM_HOSTNAME}${currentPortSuffix()}`
}

export function schoolSiteUrl(schoolSlug: string, path = '/'): string {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${schoolSiteOrigin(schoolSlug)}${normalized}`
}

/** Display a current-app hostname, preserving explicit custom domains. */
export function schoolDisplayHost(school: { slug: string; domain?: string }): string {
  const dnsLabel = school.slug.replaceAll('.', '-')
  // Old seed records stored hostnames such as london.telugu.localhost. They are
  // derived from the old slug, not explicit custom domains, so show the current
  // hyphenated hostname instead.
  if (school.domain && !school.domain.startsWith(`${school.slug}.`)) return school.domain
  return `${dnsLabel}${TENANT_HOST_SUFFIX}.${APP_DOMAIN}`
}
