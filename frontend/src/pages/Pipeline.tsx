import { useEffect } from 'react'
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

        {status === 'loading_veille' && <Loader label="Analyse de la veille en cours…" />}

        {veille && (status === 'awaiting_human' || status === 'loading_stratege') && (
          <VeilleResult data={veille} />
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
