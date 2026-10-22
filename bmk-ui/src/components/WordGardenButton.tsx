import { useAuth } from '../auth/AuthContext'

type Props = {
  className?: string
  short?: boolean
}

export default function WordGardenButton({
  className = 'home-btn',
  short = false,
}: Props) {
  const { accessToken } = useAuth()

  const handleOpen = () => {
    const baseUrl = (import.meta.env.VITE_VOCABULARY_PLATFORM_URL || 'http://localhost:8380').replace(/\/$/, '')
    const token = accessToken || localStorage.getItem('access_token') || ''
    const returnTo = window.location.href

    if (token) {
      const params = new URLSearchParams()
      params.set('bmk_token', token)
      params.set('return_to', returnTo)
      window.location.assign(`${baseUrl}/sso#${params.toString()}`)
    } else {
      window.location.assign(baseUrl)
    }
  }

  return (
    <button
      type="button"
      className={className}
      onClick={handleOpen}
      title="Open the standalone Word Garden Telugu Vocabulary Platform"
    >
      {short ? '🌱 Word Garden' : '🌱 Word Garden • పదాల తోట'}
    </button>
  )
}
