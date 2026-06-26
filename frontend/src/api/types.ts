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
  tweet_count: number
  top_shares: number
  source_tweet_ids: string[]
}

export interface VeilleResultData {
  run_id: string
  is_alert: boolean
  alert_level: AlertLevel
  peaks: Peak[]
  summary: string
  threshold_breaches: Record<string, unknown>
  is_mock: boolean
}

export interface StrategeOption {
  option_id: string
  titre: string
  tonalite: Tonalite
  description: string
  risques: string[]
  source_tweet_ids: string[]
}

export interface StrategeResultData {
  run_id: string
  options: StrategeOption[]
  option_recommandee: string
  justification: string
}

export interface DraftVersion {
  titre: string
  tonalite: Tonalite
  corps: string
  call_to_action: string
  source_tweet_ids: string[]
}

export interface RedacteurResultData {
  run_id: string
  versions: DraftVersion[]
  recommandation: string
}

export interface SessionSummary {
  run_id: string
  status: string
  alert_level: string | null
  created_at: string
}

export interface SessionDetail {
  run_id: string
  status: string
  is_mock: boolean
  alerts: Record<string, unknown> | null
  strategy_options: Record<string, unknown> | null
  draft_response: Record<string, unknown> | null
}
