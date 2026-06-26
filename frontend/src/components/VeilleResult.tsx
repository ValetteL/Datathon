import type { VeilleResultData } from '../api/types'
import PeaksTable from './PeaksTable'

interface VeilleResultProps {
  data: VeilleResultData
}

export default function VeilleResult({ data }: VeilleResultProps) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-[var(--text)]">{data.summary}</p>
      <div>
        <p className="mb-2 text-sm font-medium text-[var(--text-h)]">Pics détectés</p>
        <PeaksTable peaks={data.peaks} />
      </div>
    </div>
  )
}
