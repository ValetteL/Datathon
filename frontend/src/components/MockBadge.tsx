interface MockBadgeProps {
  isMock: boolean
}

// US-03 : signale que les narratifs sont simulés (AgentAnalyste non branché)
export default function MockBadge({ isMock }: MockBadgeProps) {
  if (!isMock) return null

  return (
    <div className="flex items-center gap-2 rounded-lg border border-yellow-300 bg-yellow-100 px-4 py-2 text-sm text-yellow-900">
      <span aria-hidden="true">⚠</span>
      <span>Narratifs simulés — AgentAnalyste non branché</span>
    </div>
  )
}
