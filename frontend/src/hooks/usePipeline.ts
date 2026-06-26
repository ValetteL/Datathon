import { useCallback, useState } from 'react'
import {
  lancerRedacteur,
  lancerStratege,
  lancerVeille,
  listerSessions,
  recupererSession,
  PipelineApiError,
  type PipelineStep,
} from '../api/client'
import type {
  RedacteurResultData,
  SessionDetail,
  SessionSummary,
  StrategeResultData,
  VeilleResultData,
} from '../api/types'

export interface PipelineError {
  step: PipelineStep
  message: string
}

export interface PipelineState {
  status: string
  runId: string | null
  veille: VeilleResultData | null
  stratege: StrategeResultData | null
  redacteur: RedacteurResultData | null
  error: PipelineError | null
  sessions: SessionSummary[]
  sessionsLoading: boolean
}

const LOADING_STATUSES = ['loading_veille', 'loading_stratege', 'loading_redacteur']

const initialState: PipelineState = {
  status: 'idle',
  runId: null,
  veille: null,
  stratege: null,
  redacteur: null,
  error: null,
  sessions: [],
  sessionsLoading: false,
}

function veilleFromDetail(detail: SessionDetail): VeilleResultData | null {
  if (!detail.alerts) return null
  return {
    run_id: detail.run_id,
    is_alert: detail.alerts['is_alert'] as boolean,
    alert_level: detail.alerts['alert_level'] as VeilleResultData['alert_level'],
    peaks: (detail.alerts['peaks'] ?? []) as VeilleResultData['peaks'],
    summary: detail.alerts['summary'] as string,
    threshold_breaches: (detail.alerts['threshold_breaches'] ?? {}) as Record<string, unknown>,
    is_mock: detail.is_mock,
  }
}

function strategeFromDetail(detail: SessionDetail): StrategeResultData | null {
  if (!detail.strategy_options) return null
  return {
    run_id: detail.run_id,
    options: (detail.strategy_options['options'] ?? []) as StrategeResultData['options'],
    option_recommandee: detail.strategy_options['option_recommandee'] as string,
    justification: detail.strategy_options['justification'] as string,
  }
}

function redacteurFromDetail(detail: SessionDetail): RedacteurResultData | null {
  if (!detail.draft_response) return null
  return {
    run_id: detail.run_id,
    versions: (detail.draft_response['versions'] ?? []) as RedacteurResultData['versions'],
    recommandation: detail.draft_response['recommandation'] as string,
  }
}

export function usePipeline() {
  const [state, setState] = useState<PipelineState>(initialState)

  const isLoading = LOADING_STATUSES.includes(state.status)

  // US-01 : lancer l'analyse de Veille
  const lancerAnalyse = useCallback(async () => {
    if (LOADING_STATUSES.includes(state.status)) return // garde anti double-clic
    setState((s) => ({ ...s, status: 'loading_veille', error: null }))
    try {
      const veille = await lancerVeille()
      setState((s) => ({
        ...s,
        status: 'veille_done',
        runId: veille.run_id,
        veille,
      }))
      // Une fois la Veille affichée, on attend la décision humaine.
      setState((s) => ({ ...s, status: 'awaiting_human' }))
    } catch (error) {
      setState((s) => ({
        ...s,
        status: 'idle',
        error: toPipelineError(error, 'veille'),
      }))
    }
  }, [state.status])

  // US-04 : validation humaine
  const valider = useCallback(async () => {
    if (!state.runId || isLoading) return
    setState((s) => ({ ...s, status: 'loading_stratege', error: null }))
    try {
      const stratege = await lancerStratege(state.runId, true)
      setState((s) => ({ ...s, status: 'stratege_done', stratege }))
      setState((s) => ({ ...s, status: 'loading_redacteur' }))
      const redacteur = await lancerRedacteur(state.runId)
      setState((s) => ({ ...s, status: 'complete', redacteur }))
    } catch (error) {
      setState((s) => ({
        ...s,
        status: 'awaiting_human',
        error: toPipelineError(error, 'stratege'),
      }))
    }
  }, [state.runId, isLoading])

  const rejeter = useCallback(() => {
    if (isLoading) return
    setState((s) => ({ ...s, status: 'rejected' }))
  }, [isLoading])

  // US-09 : liste des sessions précédentes
  const chargerSessions = useCallback(async () => {
    setState((s) => ({ ...s, sessionsLoading: true }))
    try {
      const sessions = await listerSessions()
      setState((s) => ({ ...s, sessions, sessionsLoading: false }))
    } catch (error) {
      setState((s) => ({
        ...s,
        sessionsLoading: false,
        error: toPipelineError(error, 'sessions'),
      }))
    }
  }, [])

  // US-08 : retry de l'étape en erreur uniquement
  const retry = useCallback(() => {
    if (!state.error) return
    const step = state.error.step
    setState((s) => ({ ...s, error: null }))
    if (step === 'veille') {
      void lancerAnalyse()
    } else if (step === 'stratege' || step === 'redacteur') {
      void valider()
    } else if (step === 'sessions') {
      void chargerSessions()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.error, lancerAnalyse, valider, chargerSessions])

  const ouvrirSession = useCallback(async (runId: string) => {
    setState((s) => ({ ...s, error: null }))
    try {
      const detail = await recupererSession(runId)
      setState((s) => ({
        ...s,
        runId: detail.run_id,
        status: detail.status,
        veille: veilleFromDetail(detail),
        stratege: strategeFromDetail(detail),
        redacteur: redacteurFromDetail(detail),
      }))
    } catch (error) {
      setState((s) => ({ ...s, error: toPipelineError(error, 'sessions') }))
    }
  }, [])

  const reset = useCallback(() => setState(initialState), [])

  return {
    ...state,
    isLoading,
    lancerAnalyse,
    valider,
    rejeter,
    retry,
    chargerSessions,
    ouvrirSession,
    reset,
  }
}

function toPipelineError(error: unknown, fallbackStep: PipelineStep): PipelineError {
  if (error instanceof PipelineApiError) {
    return { step: error.step, message: error.message }
  }
  if (error instanceof Error) {
    return { step: fallbackStep, message: error.message }
  }
  return { step: fallbackStep, message: 'Erreur inconnue' }
}
