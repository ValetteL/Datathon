import type { Peak } from '../api/types'

interface PeaksTableProps {
  peaks: Peak[]
}

export default function PeaksTable({ peaks }: PeaksTableProps) {
  const sorted = [...peaks].sort((a, b) => b.volume - a.volume)

  if (sorted.length === 0) {
    return <p className="text-sm text-[var(--text)]">Aucun pic détecté.</p>
  }

  return (
    <table className="w-full border-collapse overflow-hidden rounded-lg border border-[var(--border)] text-left text-sm">
      <thead className="bg-[var(--code-bg)]">
        <tr>
          <th className="px-3 py-2">Date</th>
          <th className="px-3 py-2">Volume</th>
          <th className="px-3 py-2">Top partages</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((peak) => (
          <tr key={peak.date} className="border-t border-[var(--border)]">
            <td className="px-3 py-2">{peak.date}</td>
            <td className="px-3 py-2 font-medium">{peak.volume.toLocaleString('fr-FR')}</td>
            <td className="px-3 py-2">{peak.top_shares.join(', ')}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
