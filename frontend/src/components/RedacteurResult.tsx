import { useState } from 'react'
import type { RedacteurResultData } from '../api/types'

interface RedacteurResultProps {
  data: RedacteurResultData
}

export default function RedacteurResult({ data }: RedacteurResultProps) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border border-[var(--border)] p-4 text-left">
      <h2 className="text-xl font-semibold text-[var(--text-h)]">Versions du communiqué</h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {data.versions.map((draft) => (
          <DraftCard
            key={draft.tonalite}
            draft={draft}
            recommandee={draft.tonalite === data.recommandation}
          />
        ))}
      </div>
    </section>
  )
}

function DraftCard({
  draft,
  recommandee,
}: {
  draft: RedacteurResultData['versions'][number]
  recommandee: boolean
}) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(draft.corps)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // L'API clipboard peut être indisponible (contexte non sécurisé, etc.)
    }
  }

  return (
    <div className="relative flex flex-col gap-2 rounded-lg border border-[var(--border)] p-4">
      {recommandee && (
        <span className="absolute -top-3 right-3 rounded-full bg-[var(--accent)] px-2 py-0.5 text-xs text-white">
          ⭐ Recommandée
        </span>
      )}
      <h3 className="font-semibold text-[var(--text-h)]">{draft.titre}</h3>
      <span className="text-xs uppercase tracking-wide text-[var(--text)]">{draft.tonalite}</span>
      <p className="whitespace-pre-wrap text-sm text-[var(--text)]">{draft.corps}</p>
      <p className="text-sm font-medium text-[var(--text-h)]">{draft.call_to_action}</p>
      <button
        type="button"
        onClick={handleCopy}
        className="mt-2 self-start rounded-lg border border-[var(--border)] px-3 py-1 text-sm transition hover:bg-[var(--code-bg)]"
      >
        {copied ? 'Copié ✓' : 'Copier'}
      </button>
    </div>
  )
}
