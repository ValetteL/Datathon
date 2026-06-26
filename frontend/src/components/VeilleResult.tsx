import type { VeilleResultData } from '../api/types'
import AlertBadge from './AlertBadge'
import MockBadge from './MockBadge'
import PeaksTable from './PeaksTable'

interface VeilleResultProps {
  data: VeilleResultData
}

export default function VeilleResult({ data }: VeilleResultProps) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border border-[var(--border)] p-4 text-left">
      <MockBadge isMock={data.is_mock} />

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-[var(--text-h)]">Résultats de la Veille</h2>
        <AlertBadge level={data.alert_level} />
      </div>

      <p className="text-[var(--text)]">{data.summary}</p>

      <div>
        <h3 className="mb-2 font-medium text-[var(--text-h)]">Pics détectés</h3>
        <PeaksTable peaks={data.peaks} />
      </div>
    </section>
  )
}
