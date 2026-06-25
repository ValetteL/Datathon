"""
Contrat Pydantic de l'AgentAnalyste (Ruben, P3).

Règles (AD-5) :
  - source_tweet_ids obligatoire (anti-hallucination)
  - Pydantic v2 — utiliser model_dump() pour sérialiser dans CrisisState

Note : StrategyOptions → src/agents/stratege.py (Baptiste)
       DraftCommunique → src/agents/redacteur.py (Baptiste)
"""
from __future__ import annotations
from pydantic import BaseModel, Field


class NarrativeEntry(BaseModel):
    label: str = Field(description="Nom du narratif (ex: 'Extrême Droite / Politique')")
    volume: int = Field(description="Nombre de tweets classés dans ce narratif")
    exemples: list[str] = Field(description="2-3 verbatims représentatifs du narratif")


class ActeurCle(BaseModel):
    compte: str = Field(description="Nom ou handle du compte")
    type: str = Field(description="Type : media | influenceur | institution | militant | anonyme")
    volume_tweets: int = Field(description="Nombre de tweets de ce compte dans le corpus")


class NarrativeResult(BaseModel):
    """Output de l'AgentAnalyste — ce que CrisisState['narratives'] doit contenir."""
    narratif_dominant: str = Field(
        description="Narratif le plus représenté en volume de tweets"
    )
    repartition: list[NarrativeEntry] = Field(
        description="Distribution complète des narratifs, du plus au moins fréquent"
    )
    acteurs_cles: list[ActeurCle] = Field(
        description="Top 10 comptes par volume, avec leur type"
    )
    tweets_seeds: list[str] = Field(
        description="postIDs des tweets qui ont déclenché chaque vague principale"
    )
    resume_analytique: str = Field(
        description=(
            "Synthèse factuelle en 3-5 phrases : qui parle, de quoi, avec quelle intensité. "
            "Ton neutre — décrire sans juger (AD-4)."
        )
    )
    source_tweet_ids: list[str] = Field(
        description="postIDs des tweets utilisés pour produire cette analyse (AD-5)"
    )
