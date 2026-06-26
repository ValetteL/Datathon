// Types partagés pour le pipeline multi-agents

export type AlertLevel = 'low' | 'medium' | 'high' | 'critical'

export type Tonalite = 'prudent' | 'equilibre' | 'assertif'

export type SessionStatus =
  | 'idle'
  | 'loading_veille'
  | 'veille_done'
  | 'awaiting_human'
  | 'loading_stratege'
  | 'stratege_done'
  | 'loading_redacteur'
  | 'complete'
  | 'rejected'

export interface Peak {
  date: string
  volume: number
  top_shares: string[]
}

export interface VeilleMetrics {
  tweets_viraux: number
  pic_journalier: number
  pic_horaire: number
}

export interface VeilleResultData {
  run_id: string
  alert_level: AlertLevel
  summary: string
  peaks: Peak[]
  metrics: VeilleMetrics
  is_mock: boolean
}

export interface StrategeOption {
  id: string
  titre: string
  tonalite: Tonalite
  description: string
  risques: string[]
}

export interface StrategeResultData {
  options: StrategeOption[]
  option_recommandee: string
  justification: string
}

export interface RedacteurDraft {
  id: string
  titre: string
  tonalite: Tonalite
  corps: string
  call_to_action: string
}

export interface RedacteurResultData {
  drafts: RedacteurDraft[]
  version_recommandee: string
}

export interface SessionSummary {
  run_id: string
  status: SessionStatus
  alert_level: AlertLevel | null
  created_at: string
}

export interface SessionDetail extends SessionSummary {
  veille: VeilleResultData | null
  stratege: StrategeResultData | null
  redacteur: RedacteurResultData | null
}
