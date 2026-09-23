import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { fetchMe, login as loginRequest } from '../api/auth'
import type { User } from '../types/auth'

interface AuthContextValue {
  user: User | null
  accessToken: string | null
  loading: boolean
  login: (username: string, password: string) => Promise<User>
  logout: () => void
  setUserProfile: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function readStoredUser(): User | null {
  const raw = localStorage.getItem('bmk_user')
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => readStoredUser())
  const [accessToken, setAccessToken] = useState<string | null>(
    () => localStorage.getItem('access_token'),
  )
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    fetchMe()
      .then((profile) => {
        setUser(profile)
        localStorage.setItem('bmk_user', JSON.stringify(profile))
      })
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('bmk_user')
        setUser(null)
        setAccessToken(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const data = await loginRequest(username, password)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('bmk_user', JSON.stringify(data.user))
    setAccessToken(data.access)
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('bmk_user')
    setAccessToken(null)
    setUser(null)
  }, [])

  const setUserProfile = useCallback((profile: User) => {
    setUser(profile)
    localStorage.setItem('bmk_user', JSON.stringify(profile))
  }, [])

  const value = useMemo(
    () => ({ user, accessToken, loading, login, logout, setUserProfile }),
    [user, accessToken, loading, login, logout, setUserProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
