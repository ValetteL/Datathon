from __future__ import annotations
from typing import TypedDict, Optional
import pandas as pd


class CrisisState(TypedDict):
    # Données brutes
    raw_df: pd.DataFrame
    tweets_sample: pd.DataFrame
    corpus_config: dict  # {"evenement": str, "periode": str, "mots_cles": list[str]}

    # Output AgentAnalyste
    narratives: Optional[dict]   # NarrativeResult.model_dump()

    # Output AgentVeille
    alerts: Optional[dict]       # AlertSignal.model_dump()

    # Validation humaine
    human_approved: bool

    # Output AgentStratège
    strategy_options: Optional[dict]

    # Output AgentRédacteur
    draft_response: Optional[dict]

    # Métadonnées
    run_id: str
    errors: list[str]
