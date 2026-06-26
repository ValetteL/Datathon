import type { AnalysteResultData } from '../api/types'

const NARRATIF_LABELS: Record<string, string> = {
  censure: 'Censure',
  copinage: 'Copinage',
  defense_ultia: 'Défense Ultia',
  defense_cnc: 'Défense CNC',
  autre: 'Autre',
}

interface AnalysteResultProps {
  data: AnalysteResultData
}

export default function AnalysteResult({ data }: AnalysteResultProps) {
  const total = Object.values(data.repartition).reduce((a, b) => a + b, 0) || 1
  const sorted = Object.entries(data.repartition).sort(([, a], [, b]) => b - a)

  return (
    <section className="flex flex-col gap-4 rounded-xl border border-[var(--border)] p-4 text-left">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-[var(--text-h)]">Analyse des narratifs</h2>
        <span className="text-sm text-[var(--text)]">{data.tweet_count} tweets classifiés</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {sorted.map(([narratif, count]) => {
          const pct = Math.round((count / total) * 100)
          const isDominant = narratif === data.narratif_dominant
          return (
            <div key={narratif}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span
                  className={
                    isDominant
                      ? 'font-medium text-[var(--text-h)]'
                      : 'text-[var(--text)]'
                  }
                >
                  {NARRATIF_LABELS[narratif] ?? narratif}
                  {isDominant && (
                    <span className="ml-2 rounded-full bg-[var(--accent-bg)] px-2 py-0.5 text-xs font-medium text-[var(--accent)]">
                      dominant
                    </span>
                  )}
                </span>
                <span className="tabular-nums text-[var(--text)]">
                  {pct}%
                  <span className="ml-1 text-xs opacity-60">({count})</span>
                </span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--code-bg)]">
                <div
                  className="h-1.5 rounded-full bg-[var(--accent)] transition-all"
                  style={{ width: `${pct}%`, opacity: isDominant ? 1 : 0.35 }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {data.errors.length > 0 && (
        <p className="text-xs text-yellow-600">
          ⚠ {data.errors.length} batch(es) en erreur — résultats partiels
        </p>
      )}
    </section>
  )
}
