import type { AlertLevel } from '../api/types'

const STYLES: Record<AlertLevel, { label: string; classes: string }> = {
  low: { label: 'Faible', classes: 'bg-green-100 text-green-800 border-green-300' },
  medium: { label: 'Moyen', classes: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
  high: { label: 'Élevé', classes: 'bg-orange-100 text-orange-800 border-orange-300' },
  critical: { label: 'Critique', classes: 'bg-red-100 text-red-800 border-red-300' },
}

interface AlertBadgeProps {
  level: AlertLevel
}

export default function AlertBadge({ level }: AlertBadgeProps) {
  const style = STYLES[level]
  return (
    <span
      data-level={level}
      className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium ${style.classes}`}
    >
      Niveau d'alerte : {style.label}
    </span>
  )
}
