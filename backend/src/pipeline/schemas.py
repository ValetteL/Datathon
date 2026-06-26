"""
Contrats Pydantic des agents J2 — interfaces fixes entre les agents du pipeline.

Règles (AD-5) :
  - source_tweet_ids obligatoire dans chaque output (anti-hallucination)
  - Chaque champ est documenté pour guider le LLM via PydanticOutputParser
  - Pydantic v2 — utiliser model_dump() pour sérialiser dans CrisisState
"""
from __future__ import annotations
from pydantic import BaseModel, Field


# ── AgentAnalyste (Ruben, P3) ─────────────────────────────────────────────────

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


# ── AgentStratège (Baptiste, P5) ──────────────────────────────────────────────

class StrategyOption(BaseModel):
    nom: str = Field(description="Nom court de l'option (ex: 'Réponse factuelle')")
    description: str = Field(description="Description de l'approche en 2-3 phrases")
    ton: str = Field(description="Ton dominant : factuel | empathique | ferme | silence")
    avantages: list[str] = Field(description="2-3 points forts de cette option")
    risques: list[str] = Field(description="2-3 risques ou limites identifiés")

class StrategyOptions(BaseModel):
    """Output de l'AgentStratège — ce que CrisisState['strategy_options'] doit contenir."""
    options: list[StrategyOption] = Field(
        description="Exactement 3 options de réponse distinctes, ordonnées du plus au moins conservateur",
        min_length=3,
        max_length=3,
    )
    recommandation: str = Field(
        description=(
            "Nom de l'option recommandée et justification en 1-2 phrases. "
            "La décision finale reste humaine (AD-7)."
        )
    )
    contexte_utilise: str = Field(
        description="Résumé du contexte de crise qui a guidé les options (narratif dominant, niveau d'alerte)"
    )
    source_tweet_ids: list[str] = Field(
        description="postIDs des tweets pris en compte pour construire ces options (AD-5)"
    )


# ── AgentRédacteur (Baptiste, P5) ─────────────────────────────────────────────

class ResponseDraft(BaseModel):
    option_nom: str = Field(description="Nom de l'option de stratégie correspondante")
    titre: str = Field(description="Titre ou objet du communiqué / tweet")
    corps: str = Field(
        description=(
            "Texte complet du draft de réponse. "
            "Ton institutionnel, neutre, factuel. Jamais de jugement politique (AD-4)."
        )
    )
    format: str = Field(description="Format cible : tweet | communique | thread | email")
    longueur_chars: int = Field(description="Longueur réelle du corps en caractères")
    neutralite_validee: bool = Field(
        description="True si le texte respecte NEUTRALITY_SYSTEM_PROMPT — auto-vérifié par le rédacteur"
    )

class DraftResponse(BaseModel):
    """Output de l'AgentRédacteur — ce que CrisisState['draft_response'] doit contenir."""
    drafts: list[ResponseDraft] = Field(
        description="Un draft par option stratégique soumise"
    )
    avertissements: list[str] = Field(
        description=(
            "Points de vigilance éditoriaux : tournures à risque, ambiguïtés, "
            "éléments factuels à vérifier avant publication"
        )
    )
    source_tweet_ids: list[str] = Field(
        description="postIDs des tweets cités ou paraphrasés dans les drafts (AD-5)"
    )
