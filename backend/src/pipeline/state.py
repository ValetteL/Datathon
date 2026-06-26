from __future__ import annotations
from typing import TypedDict, Optional
import pandas as pd


class CrisisState(TypedDict):
    # Données brutes
    raw_df: pd.DataFrame
    tweets_sample: pd.DataFrame
    corpus_config: dict  # {"evenement": str, "periode": str, "mots_cles": list[str]}

    # Output AgentAnalyste → pipeline.schemas.NarrativeResult.model_dump()
    narratives: Optional[dict]

    # Output AgentVeille → agents.veille.AlertSignal.model_dump()
    alerts: Optional[dict]

    # Validation humaine (HumanGate — AD-7)
    human_approved: bool

    # Output AgentStratège → pipeline.schemas.StrategyOptions.model_dump()
    strategy_options: Optional[dict]

    # Output AgentRédacteur → pipeline.schemas.DraftResponse.model_dump()
    draft_response: Optional[dict]

    # Métadonnées
    run_id: str
    errors: list[str]
