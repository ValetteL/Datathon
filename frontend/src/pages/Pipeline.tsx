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
  } = usePipeline()

  // US-09 : charger les sessions précédentes au montage
  useEffect(() => {
    void chargerSessions()
  }, [chargerSessions])

  const pipelineStarted = status !== 'idle'

  return (
    <div className="flex flex-col gap-6 pb-16">
      {pipelineStarted && <StepIndicator status={status} />}

      <header className="px-6 pt-8 text-center">
        <h1 className="text-3xl font-semibold text-[var(--text-h)]">
          Pipeline d'analyse de crise virale
        </h1>
        <p className="mt-2 text-[var(--text)]">CNC × Ultia — démonstration multi-agents</p>
      </header>

      <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4">
        {error && <ErrorBanner error={error} onRetry={retry} />}

        {!pipelineStarted && (
          <>
            <div className="flex justify-center">
              <button
                type="button"
                onClick={lancerAnalyse}
                disabled={isLoading}
                className="rounded-lg bg-[var(--accent)] px-6 py-3 font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50 hover:opacity-90"
              >
                Lancer l'analyse
              </button>
            </div>

            <section className="flex flex-col gap-3 text-left">
              <h2 className="text-lg font-semibold text-[var(--text-h)]">Sessions précédentes</h2>
              <SessionsList
                sessions={sessions}
                loading={sessionsLoading}
                onSelect={ouvrirSession}
              />
            </section>
          </>
        )}

        {status === 'loading_veille' && <Loader label="Analyse de la Veille en cours…" />}

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
          <div className="rounded-xl border border-[var(--border)] p-5 text-center text-[var(--text)]">
            Analyse rejetée. Le pipeline s'est arrêté avant la génération de réponses.
          </div>
        )}
      </main>
    </div>
  )
}
