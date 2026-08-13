import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    // Let the browser set multipart boundary.
    if (config.headers && 'Content-Type' in config.headers) {
      delete config.headers['Content-Type']
    }
  }
  const url = config.url ?? ''
  const isPublic = url.includes('/api/public/')
  if (!isPublic) {
    const access = localStorage.getItem('access_token')
    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined
    if (error.response?.status === 401 && original && !original._retry) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        original._retry = true
        try {
          const { data } = await axios.post<{ access: string }>(
            `${API_BASE_URL}/api/auth/refresh/`,
            { refresh },
          )
          localStorage.setItem('access_token', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('bmk_user')
        }
      }
    }
    return Promise.reject(error)
  },
)
