import { useState } from 'react'

interface CollapsibleCardProps {
  title: string
  summary: string
  badge?: React.ReactNode
  defaultOpen?: boolean
  children: React.ReactNode
}

export default function CollapsibleCard({
  title,
  summary,
  badge,
  defaultOpen = true,
  children,
}: CollapsibleCardProps) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--border)]">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition hover:bg-[var(--code-bg)]"
      >
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <span className="shrink-0 font-medium text-[var(--text-h)]">{title}</span>
          {badge}
          {!open && (
            <span className="truncate text-sm text-[var(--text)] opacity-70">— {summary}</span>
          )}
        </div>
        <svg
          className={`h-4 w-4 shrink-0 text-[var(--text)] transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && <div className="border-t border-[var(--border)] p-4">{children}</div>}
    </div>
  )
}
