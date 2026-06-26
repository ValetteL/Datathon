from pydantic import BaseModel


class AnalysteResponse(BaseModel):
    run_id: str
    narratif_dominant: str
    repartition: dict
    tweet_count: int
    errors: list[str]


class PeakResponse(BaseModel):
    date: str
    tweet_count: int
    top_shares: int
    source_tweet_ids: list[str]


class VeilleResponse(BaseModel):
    run_id: str
    is_alert: bool
    alert_level: str
    peaks: list[PeakResponse]
    summary: str
    threshold_breaches: dict
    is_mock: bool


class ResponseOptionResponse(BaseModel):
    option_id: str
    titre: str
    description: str
    tonalite: str
    risques: list[str]
    source_tweet_ids: list[str]


class StrategeResponse(BaseModel):
    run_id: str
    options: list[ResponseOptionResponse]
    option_recommandee: str
    justification: str


class DraftVersionResponse(BaseModel):
    tonalite: str
    titre: str
    corps: str
    call_to_action: str
    source_tweet_ids: list[str]


class RedacteurResponse(BaseModel):
    run_id: str
    versions: list[DraftVersionResponse]
    recommandation: str


class SessionSummary(BaseModel):
    run_id: str
    status: str
    alert_level: str | None
    created_at: str


class SessionDetail(BaseModel):
    run_id: str
    status: str
    narratives: dict | None
    alerts: dict | None
    strategy_options: dict | None
    draft_response: dict | None
