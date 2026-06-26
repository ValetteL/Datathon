import type { SessionSummary } from '../api/types'
import AlertBadge from './AlertBadge'

const STATUS_LABELS: Record<string, string> = {
  idle: 'Nouvelle',
  loading_veille: 'Veille en cours',
  veille_done: 'Veille terminée',
  awaiting_human: 'En attente de validation',
  loading_stratege: 'Stratège en cours',
  stratege_done: 'Stratège terminé',
  loading_redacteur: 'Rédacteur en cours',
  complete: 'Terminée',
  rejected: 'Rejetée',
}

interface SessionsListProps {
  sessions: SessionSummary[]
  loading: boolean
  onSelect: (runId: string) => void
}

// US-09 : reprendre une session existante
export default function SessionsList({ sessions, loading, onSelect }: SessionsListProps) {
  if (loading) {
    return <p className="text-sm text-[var(--text)]">Chargement des sessions…</p>
  }

  if (sessions.length === 0) {
    return <p className="text-sm text-[var(--text)]">Aucune session disponible.</p>
  }

  return (
    <ul className="flex flex-col gap-2">
      {sessions.map((session) => (
        <li key={session.run_id}>
          <button
            type="button"
            onClick={() => onSelect(session.run_id)}
            className="flex w-full items-center justify-between gap-3 rounded-lg border border-[var(--border)] px-4 py-2 text-left text-sm transition hover:bg-[var(--code-bg)]"
          >
            <span className="font-mono text-[var(--text-h)]">
              {session.run_id.slice(0, 8)}
            </span>
            <span className="text-[var(--text)]">
              {STATUS_LABELS[session.status] ?? session.status}
            </span>
            {session.alert_level && <AlertBadge level={session.alert_level} />}
            <span className="text-[var(--text)]">
              {new Date(session.created_at).toLocaleString('fr-FR')}
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
