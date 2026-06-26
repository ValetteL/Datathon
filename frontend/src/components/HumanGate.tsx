interface HumanGateProps {
  onValider: () => void
  onRejeter: () => void
  disabled: boolean
}

export default function HumanGate({ onValider, onRejeter, disabled }: HumanGateProps) {
  return (
    <section className="overflow-hidden rounded-xl border border-[var(--accent-border)] bg-[var(--accent-bg)]">
      <div className="h-1 bg-[var(--accent)]" />
      <div className="flex flex-col gap-5 p-6">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 text-xl" aria-hidden>
            🛡
          </span>
          <div className="flex flex-col gap-1">
            <p className="font-semibold text-[var(--text-h)]">Validation humaine requise</p>
            <p className="text-sm text-[var(--text)]">
              La veille signale une situation à risque. Confirmez pour déclencher la génération
              automatique des options stratégiques et des communiqués de presse institutionnels.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <button
            type="button"
            onClick={onValider}
            disabled={disabled}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-[var(--accent)] px-6 py-3 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50 hover:opacity-90"
          >
            Générer la stratégie de réponse
            <span aria-hidden>→</span>
          </button>
          <button
            type="button"
            onClick={onRejeter}
            disabled={disabled}
            className="flex items-center justify-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-5 py-3 text-sm font-medium text-[var(--text)] transition disabled:cursor-not-allowed disabled:opacity-50 hover:bg-[var(--code-bg)]"
          >
            Arrêter l'analyse
          </button>
        </div>

        <p className="text-xs text-[var(--text)] opacity-60">
          Cette action déclenche les agents Stratège et Rédacteur — elle ne peut pas être annulée.
        </p>
      </div>
    </section>
  )
}
