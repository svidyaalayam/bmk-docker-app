/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_APP_DOMAIN?: string
  readonly VITE_TENANT_HOST_SUFFIX?: string
  readonly VITE_PLATFORM_HOSTNAME?: string
  readonly VITE_SIKSHAVAHINI_URL?: string
  readonly VITE_SUNAADAM_URL?: string
  /** local | test | staging | production */
  readonly VITE_APP_ENV?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
