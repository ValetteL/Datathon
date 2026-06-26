import { useEffect } from 'react'
import AlertBadge from '../components/AlertBadge'
import AnalysteResult from '../components/AnalysteResult'
import CollapsibleCard from '../components/CollapsibleCard'
import ErrorBanner from '../components/ErrorBanner'
import HumanGate from '../components/HumanGate'
import Loader from '../components/Loader'
import RedacteurResult from '../components/RedacteurResult'
import SessionsList from '../components/SessionsList'
import StepIndicator from '../components/StepIndicator'
import StrategeResult from '../components/StrategeResult'
import VeilleResult from '../components/VeilleResult'
import { usePipeline } from '../hooks/usePipeline'

export default function Pipeline() {
  const {
    status,
    analyste,
    veille,
    stratege,
    redacteur,
    error,
    sessions,
    sessionsLoading,
    isLoading,
    lancerAnalyse,
    valider,
    rejeter,
    retry,
    chargerSessions,
    ouvrirSession,
    reset,
  } = usePipeline()

  useEffect(() => {
    void chargerSessions()
  }, [chargerSessions])

  const pipelineStarted = status !== 'idle'
  const isTerminal = status === 'complete' || status === 'rejected'

  // Résumés pour les en-têtes repliés
  const analyteSummary = analyste
    ? `${analyste.narratif_dominant} dominant · ${analyste.tweet_count} tweets`
    : ''
  const veilleLevel = veille?.alert_level ?? 'low'
  const veilleSummary = veille
    ? `${veille.peaks.length} pic(s) · ${veille.summary.slice(0, 70)}…`
    : ''

  return (
    <div className="flex min-h-svh flex-col">
      {pipelineStarted && <StepIndicator status={status} />}

      <header className="border-b border-[var(--border)] bg-[var(--bg)] px-6 py-3">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="text-left">
            <h1 className="text-xl font-semibold text-[var(--text-h)]">
              Pipeline d'analyse de crise
            </h1>
            <p className="text-sm text-[var(--text)]">CNC × Ultia — démonstration multi-agents</p>
          </div>
          {isTerminal && (
            <button
              type="button"
              onClick={reset}
              className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-4 py-2 text-sm font-medium text-[var(--text)] transition hover:bg-[var(--code-bg)]"
            >
              ← Nouvelle analyse
            </button>
          )}
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-4 px-4 py-4">
        {error && <ErrorBanner error={error} onRetry={retry} />}

        {!pipelineStarted && (
          <>
            <div className="flex justify-center">
              <button
                type="button"
                onClick={lancerAnalyse}
                disabled={isLoading}
                className="rounded-lg bg-[var(--accent)] px-8 py-3 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50 hover:opacity-90"
              >
                Lancer l'analyse
              </button>
            </div>

            <section className="flex flex-col gap-3 text-left">
              <h2 className="text-base font-semibold text-[var(--text-h)]">Sessions précédentes</h2>
              <SessionsList
                sessions={sessions}
                loading={sessionsLoading}
                onSelect={ouvrirSession}
              />
            </section>
          </>
        )}

        {status === 'loading_analyste' && <Loader label="Classification des tweets en cours…" />}

        {/* Analyste — toujours visible, replié automatiquement quand la veille arrive */}
        {analyste && (
          <CollapsibleCard
            key={veille ? 'analyste-past' : 'analyste-current'}
            defaultOpen={!veille}
            title="Analyse des narratifs"
            summary={analyteSummary}
          >
            <AnalysteResult data={analyste} />
          </CollapsibleCard>
        )}

        {status === 'loading_veille' && <Loader label="Détection des alertes et des pics…" />}

        {/* Veille — toujours visible après la détection, replié quand la stratégie arrive */}
        {veille && (
          <CollapsibleCard
            key={stratege ? 'veille-past' : 'veille-current'}
            defaultOpen={!stratege}
            title="Résultats de la veille"
            summary={veilleSummary}
            badge={<AlertBadge level={veilleLevel} compact />}
          >
            <VeilleResult data={veille} />
          </CollapsibleCard>
        )}

        {status === 'awaiting_human' && (
          <HumanGate onValider={valider} onRejeter={rejeter} disabled={isLoading} />
        )}

        {status === 'loading_stratege' && <Loader label="Élaboration de la stratégie…" />}

        {stratege &&
          (status === 'stratege_done' ||
            status === 'loading_redacteur' ||
            status === 'complete') && <StrategeResult data={stratege} />}

        {status === 'loading_redacteur' && <Loader label="Rédaction des communiqués…" />}

        {redacteur && status === 'complete' && <RedacteurResult data={redacteur} />}

        {status === 'rejected' && (
          <div className="rounded-xl border border-[var(--border)] p-6 text-center">
            <p className="font-medium text-[var(--text-h)]">Analyse arrêtée</p>
            <p className="mt-1 text-sm text-[var(--text)]">
              Le pipeline s'est arrêté avant la génération de réponses.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
