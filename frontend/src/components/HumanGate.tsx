interface HumanGateProps {
  onValider: () => void
  onRejeter: () => void
  disabled: boolean
}

// US-04 : validation humaine avant de poursuivre le pipeline
export default function HumanGate({ onValider, onRejeter, disabled }: HumanGateProps) {
  return (
    <section className="flex flex-col items-center gap-3 rounded-xl border border-[var(--border)] p-5">
      <p className="text-[var(--text-h)]">
        Valider cette analyse pour poursuivre vers la stratégie de réponse ?
      </p>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onValider}
          disabled={disabled}
          className="rounded-lg bg-green-600 px-5 py-2 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50 hover:bg-green-700"
        >
          Valider
        </button>
        <button
          type="button"
          onClick={onRejeter}
          disabled={disabled}
          className="rounded-lg bg-red-600 px-5 py-2 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50 hover:bg-red-700"
        >
          Rejeter
        </button>
      </div>
    </section>
  )
}
