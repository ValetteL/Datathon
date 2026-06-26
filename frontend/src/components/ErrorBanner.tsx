import type { PipelineError } from '../hooks/usePipeline'

const STEP_LABELS: Record<PipelineError['step'], string> = {
  veille: 'Veille',
  stratege: 'Stratège',
  redacteur: 'Rédacteur',
  sessions: 'Sessions',
}

interface ErrorBannerProps {
  error: PipelineError
  onRetry: () => void
}

// US-08 : message d'erreur contextuel + bouton de relance ciblé
export default function ErrorBanner({ error, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900">
      <span>
        <strong>Échec de l'étape {STEP_LABELS[error.step]}</strong> — {error.message}
      </span>
      <button
        type="button"
        onClick={onRetry}
        className="shrink-0 rounded-lg border border-red-400 px-3 py-1 font-medium transition hover:bg-red-100"
      >
        Réessayer
      </button>
    </div>
  )
}
