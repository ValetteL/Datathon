import type { StrategeResultData, Tonalite } from '../api/types'

const TONALITE_CLASSES: Record<Tonalite, string> = {
  prudent: 'border-blue-300 bg-blue-50',
  equilibre: 'border-yellow-300 bg-yellow-50',
  assertif: 'border-red-300 bg-red-50',
}

interface StrategeResultProps {
  data: StrategeResultData
}

// US-05 : les 3 options de réponse proposées par l'AgentStratège
export default function StrategeResult({ data }: StrategeResultProps) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border border-[var(--border)] p-5 text-left">
      <h2 className="text-xl font-semibold text-[var(--text-h)]">Options stratégiques</h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {data.options.map((option) => {
          const recommandee = option.id === data.option_recommandee
          return (
            <div
              key={option.id}
              className={`relative flex flex-col gap-2 rounded-lg border p-4 ${TONALITE_CLASSES[option.tonalite]}`}
            >
              {recommandee && (
                <span className="absolute -top-3 right-3 rounded-full bg-[var(--accent)] px-2 py-0.5 text-xs text-white">
                  ⭐ Recommandée
                </span>
              )}
              <h3 className="font-semibold text-[var(--text-h)]">{option.titre}</h3>
              <span className="text-xs uppercase tracking-wide text-[var(--text)]">
                {option.tonalite}
              </span>
              <p className="text-sm text-[var(--text)]">{option.description}</p>
              <ul className="list-disc pl-5 text-sm text-[var(--text)]">
                {option.risques.map((risque) => (
                  <li key={risque}>{risque}</li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      <p className="text-sm text-[var(--text)]">
        <strong className="text-[var(--text-h)]">Justification : </strong>
        {data.justification}
      </p>
    </section>
  )
}
