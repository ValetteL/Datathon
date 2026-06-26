type StepState = 'pending' | 'active' | 'done'

const STEPS = [
  { key: 'veille', label: 'Veille' },
  { key: 'human', label: 'Validation' },
  { key: 'stratege', label: 'Stratège' },
  { key: 'redacteur', label: 'Rédacteur' },
] as const

const STATUS_ORDER = [
  'idle',
  'loading_veille',
  'veille_done',
  'awaiting_human',
  'loading_stratege',
  'stratege_done',
  'loading_redacteur',
  'complete',
]

function computeStepStates(status: string): Record<(typeof STEPS)[number]['key'], StepState> {
  const index = STATUS_ORDER.indexOf(status === 'rejected' ? 'awaiting_human' : status)

  const stepFor = (doneAt: string, activeAt: string): StepState => {
    const doneIndex = STATUS_ORDER.indexOf(doneAt)
    const activeIndex = STATUS_ORDER.indexOf(activeAt)
    if (index > doneIndex) return 'done'
    if (index >= activeIndex) return 'active'
    return 'pending'
  }

  return {
    veille: stepFor('veille_done', 'loading_veille'),
    human: status === 'rejected' ? 'done' : stepFor('awaiting_human', 'awaiting_human'),
    stratege: stepFor('stratege_done', 'loading_stratege'),
    redacteur: stepFor('complete', 'loading_redacteur'),
  }
}

interface StepIndicatorProps {
  status: string
}

export default function StepIndicator({ status }: StepIndicatorProps) {
  const states = computeStepStates(status)

  return (
    <div className="sticky top-0 z-10 flex items-center justify-center gap-0 border-b border-[var(--border)] bg-[var(--bg)] px-4 py-3">
      {STEPS.map((step, i) => {
        const state = states[step.key]
        return (
          <div key={step.key} className="flex items-center">
            <div className="flex items-center gap-2 px-3">
              <span
                className={[
                  'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-colors',
                  state === 'done' && 'bg-emerald-500 text-white',
                  state === 'active' && 'bg-[var(--accent)] text-white ring-4 ring-[var(--accent-bg)]',
                  state === 'pending' && 'bg-[var(--code-bg)] text-[var(--text)]',
                ]
                  .filter(Boolean)
                  .join(' ')}
              >
                {state === 'done' ? '✓' : i + 1}
              </span>
              <span
                className={[
                  'text-sm',
                  state === 'pending' && 'text-[var(--text)] opacity-50',
                  state === 'active' && 'font-medium text-[var(--text-h)]',
                  state === 'done' && 'text-[var(--text)]',
                ]
                  .filter(Boolean)
                  .join(' ')}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <span className="text-xs text-[var(--border)]">›</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
