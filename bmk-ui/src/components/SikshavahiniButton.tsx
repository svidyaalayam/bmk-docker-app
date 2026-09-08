import { useAuth } from '../auth/AuthContext'
import { dashboardPathForRole } from '../utils/routes'
import { openLessonApp } from '../utils/sikshavahini'

type Props = {
  className?: string
  short?: boolean
}

/** Opens the school's configured lesson application for the signed-in user. */
export default function SikshavahiniButton({
  className = 'linkish',
  short = false,
}: Props) {
  const { user, accessToken } = useAuth()
  if (!user || !accessToken) return null
  const app = user.lesson_app === 'sunaadam' ? 'sunaadam' : 'sikshavahini'
  const appName = app === 'sunaadam' ? 'Sunaadam' : 'Sikshavahini'

  return (
    <button
      type="button"
      className={className}
      onClick={() =>
        openLessonApp(
          app,
          accessToken,
          `${window.location.origin}${dashboardPathForRole(user.role)}`,
        )
      }
    >
      {short ? appName : `Open ${appName} lessons →`}
    </button>
  )
}
