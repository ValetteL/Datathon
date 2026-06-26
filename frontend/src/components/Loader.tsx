interface LoaderProps {
  label?: string
}

export default function Loader({ label = 'Chargement…' }: LoaderProps) {
  return (
    <div className="flex items-center justify-center gap-3 py-6 text-[var(--text)]">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--accent)]" />
      <span>{label}</span>
    </div>
  )
}
