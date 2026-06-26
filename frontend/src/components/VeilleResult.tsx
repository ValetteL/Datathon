import type { VeilleResultData } from '../api/types'
import AlertBadge from './AlertBadge'
import MockBadge from './MockBadge'
import PeaksTable from './PeaksTable'

interface VeilleResultProps {
  data: VeilleResultData
}

// US-02 : résultats de l'AgentVeille
export default function VeilleResult({ data }: VeilleResultProps) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border border-[var(--border)] p-5 text-left">
      <MockBadge isMock={data.is_mock} />

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-[var(--text-h)]">Résultats de la Veille</h2>
        <AlertBadge level={data.alert_level} />
      </div>

      <p className="text-[var(--text)]">{data.summary}</p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Metric label="Tweets viraux" value={data.metrics.tweets_viraux} />
        <Metric label="Pic journalier" value={data.metrics.pic_journalier} />
        <Metric label="Pic horaire" value={data.metrics.pic_horaire} />
      </div>

      <div>
        <h3 className="mb-2 font-medium text-[var(--text-h)]">Pics détectés</h3>
        <PeaksTable peaks={data.peaks} />
      </div>
    </section>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] px-4 py-3">
      <div className="text-2xl font-semibold text-[var(--text-h)]">
        {value.toLocaleString('fr-FR')}
      </div>
      <div className="text-sm text-[var(--text)]">{label}</div>
    </div>
  )
}
