import axios, { AxiosError } from 'axios'
import type {
  AnalysteResultData,
  RedacteurResultData,
  SessionDetail,
  SessionSummary,
  StrategeResultData,
  VeilleResultData,
} from './types'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({ baseURL })

// Nom de l'étape qui a échoué, utilisé pour afficher un message contextuel
// et permettre un retry ciblé (US-08).
export type PipelineStep = 'analyste' | 'veille' | 'stratege' | 'redacteur' | 'sessions'

export class PipelineApiError extends Error {
  step: PipelineStep

  constructor(step: PipelineStep, message: string) {
    super(message)
    this.step = step
    this.name = 'PipelineApiError'
  }
}

function toMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const err = error as AxiosError<{ detail?: unknown; message?: string }>
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      // Format d'erreur de validation FastAPI : [{loc, msg, type}]
      return detail
        .map((d) => (typeof d === 'object' && d !== null && 'msg' in d ? String((d as { msg: unknown }).msg) : String(d)))
        .join(' — ')
    }
    if (typeof detail === 'string') return detail
    return err.response?.data?.message ?? err.message ?? 'Erreur réseau inconnue'
  }
  if (error instanceof Error) return error.message
  return 'Erreur inconnue'
}

// Intercepteur global : toute erreur Axios est transformée en message lisible.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(toMessage(error))),
)

export async function lancerAnalyste(): Promise<AnalysteResultData> {
  try {
    const { data } = await apiClient.post<AnalysteResultData>('/analyse/analyste', {})
    return data
  } catch (error) {
    throw new PipelineApiError('analyste', toMessage(error))
  }
}

export async function lancerVeille(runId: string): Promise<VeilleResultData> {
  try {
    const { data } = await apiClient.post<VeilleResultData>('/analyse/veille', { run_id: runId })
    return data
  } catch (error) {
    throw new PipelineApiError('veille', toMessage(error))
  }
}

export async function lancerStratege(
  runId: string,
  humanApproved: boolean,
): Promise<StrategeResultData> {
  try {
    const { data } = await apiClient.post<StrategeResultData>('/analyse/stratege', {
      run_id: runId,
      humain_approved: humanApproved,
    })
    return data
  } catch (error) {
    throw new PipelineApiError('stratege', toMessage(error))
  }
}

export async function lancerRedacteur(runId: string): Promise<RedacteurResultData> {
  try {
    const { data } = await apiClient.post<RedacteurResultData>('/analyse/redacteur', {
      run_id: runId,
    })
    return data
  } catch (error) {
    throw new PipelineApiError('redacteur', toMessage(error))
  }
}

export async function listerSessions(): Promise<SessionSummary[]> {
  try {
    const { data } = await apiClient.get<SessionSummary[]>('/sessions')
    return data
  } catch (error) {
    throw new PipelineApiError('sessions', toMessage(error))
  }
}

export async function recupererSession(runId: string): Promise<SessionDetail> {
  try {
    const { data } = await apiClient.get<SessionDetail>(`/sessions/${runId}`)
    return data
  } catch (error) {
    throw new PipelineApiError('sessions', toMessage(error))
  }
}
