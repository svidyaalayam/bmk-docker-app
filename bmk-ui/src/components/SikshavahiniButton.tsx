type Props = {
  className?: string
  short?: boolean
}

/** Temporarily unavailable while the Sikshavahini integration is repaired. */
export default function SikshavahiniButton({
  className = 'linkish',
  short = false,
}: Props) {
  return (
    <button
      type="button"
      className={className}
      disabled
      title="Sikshavahini is temporarily unavailable."
    >
      {short ? 'Sikshavahini' : 'Sikshavahini lessons (temporarily unavailable)'}
    </button>
  )
}
