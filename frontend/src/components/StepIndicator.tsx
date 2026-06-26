import type { SessionStatus } from '../api/types'

type StepState = 'pending' | 'active' | 'done'

const STEPS = [
  { key: 'veille', label: 'Veille' },
  { key: 'human', label: 'HumanGate' },
  { key: 'stratege', label: 'Stratège' },
  { key: 'redacteur', label: 'Rédacteur' },
] as const

function computeStepStates(status: SessionStatus): Record<(typeof STEPS)[number]['key'], StepState> {
  const order: SessionStatus[] = [
    'idle',
    'loading_veille',
    'veille_done',
    'awaiting_human',
    'loading_stratege',
    'stratege_done',
    'loading_redacteur',
    'complete',
  ]
  const index = order.indexOf(status === 'rejected' ? 'awaiting_human' : status)

  const stepFor = (doneAt: SessionStatus, activeAt: SessionStatus): StepState => {
    const doneIndex = order.indexOf(doneAt)
    const activeIndex = order.indexOf(activeAt)
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
  status: SessionStatus
}

// US-07 : progression du pipeline
export default function StepIndicator({ status }: StepIndicatorProps) {
  const states = computeStepStates(status)

  return (
    <div className="sticky top-0 z-10 flex items-center justify-center gap-4 border-b border-[var(--border)] bg-[var(--bg)] py-3">
      {STEPS.map((step, i) => {
        const state = states[step.key]
        return (
          <div key={step.key} className="flex items-center gap-2">
            <span
              className={[
                'flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium',
                state === 'done' && 'bg-green-600 text-white',
                state === 'active' && 'animate-pulse bg-blue-600 text-white',
                state === 'pending' && 'bg-gray-200 text-gray-500',
              ]
                .filter(Boolean)
                .join(' ')}
            >
              {state === 'done' ? '✓' : i + 1}
            </span>
            <span
              className={
                state === 'pending' ? 'text-sm text-gray-400' : 'text-sm text-[var(--text-h)]'
              }
            >
              {step.label}
            </span>
            {i < STEPS.length - 1 && <span className="mx-1 text-[var(--border)]">—</span>}
          </div>
        )
      })}
    </div>
  )
}
