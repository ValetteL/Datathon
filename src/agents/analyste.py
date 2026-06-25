from __future__ import annotations
from collections import Counter
import pandas as pd
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from prompts.prompts import get_system_prompt, get_llm
from pipeline.state import CrisisState


# ── Schémas Pydantic ──────────────────────────────────────────────────────────

class TweetAnalysis(BaseModel):
    tweet_id: str = Field(description="postID du tweet analysé")
    narratif: str = Field(description="censure | copinage | defense_ultia | defense_cnc | autre")
    acteur_type: str = Field(description="media | militant | influenceur | anonyme | institution")
    source_tweet_ids: list[str] = Field(
        description="Liste des postID cités comme sources (au minimum le tweet_id lui-même)"
    )


class BatchResult(BaseModel):
    """Schema minimal envoyé au LLM — uniquement ce qu'il doit produire.
    Les champs agrégés (narratif_dominant, repartition) sont calculés en Python."""
    analyses: list[TweetAnalysis]


class NarrativeResult(BaseModel):
    analyses: list[TweetAnalysis]
    narratif_dominant: str = Field(description="Le narratif le plus fréquent dans l'échantillon")
    repartition: dict = Field(description="Comptage par catégorie de narratif")
    source_tweet_ids: list[str] = Field(description="Tous les postID analysés")


# ── Taxonomie et few-shot ─────────────────────────────────────────────────────

NARRATIFS_VALIDES = ["censure", "copinage", "defense_ultia", "defense_cnc", "autre"]
ACTEURS_VALIDES   = ["media", "militant", "influenceur", "anonyme", "institution"]

FEW_SHOT_EXAMPLES = """Exemples de calibration :
- "Ils censurent encore une fois la vérité, c'est inadmissible" → narratif=censure, acteur_type=militant
- "Tout le monde savait, c'est encore du copinage entre les mêmes" → narratif=copinage, acteur_type=anonyme
- "Le CNC applique simplement le règlement, rien d'anormal ici" → narratif=defense_cnc, acteur_type=institution
- "Ultia n'a rien fait de mal, on s'acharne sur eux sans preuve" → narratif=defense_ultia, acteur_type=influenceur
- "Je n'ai pas d'avis tranché, attendons d'en savoir plus" → narratif=autre, acteur_type=anonyme"""

BATCH_SIZE = 15  # borné pour tenir dans la limite d'output des modèles


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_tweets(batch: pd.DataFrame) -> str:
    lines = []
    for _, row in batch.iterrows():
        text = row.get("message_normalizer") or row.get("Full Text") or ""
        lines.append(
            f"[{row['postID']}] @{row['Author']} "
            f"(followers:{row['X Followers']}, verified:{row['X Verified']}, "
            f"type:{row['Engagement Type']})\n{text}"
        )
    return "\n\n".join(lines)


def _classify_batch(
    batch: pd.DataFrame,
    evenement: str,
    periode: str,
    llm: BaseChatModel,
    prompt: ChatPromptTemplate,
    parser: PydanticOutputParser,
) -> list[TweetAnalysis]:
    """Classifie un batch de tweets. LLM et prompt sont passés depuis run_analyste."""
    if batch.empty:
        return []

    result: BatchResult = (prompt | llm | parser).invoke({
        "evenement": evenement,
        "periode": periode,
        "narratifs": ", ".join(NARRATIFS_VALIDES),
        "acteurs": ", ".join(ACTEURS_VALIDES),
        "few_shot": FEW_SHOT_EXAMPLES,
        "tweets": _format_tweets(batch),
        "format_instructions": parser.get_format_instructions(),
    })

    return result.analyses


# ── Nœud principal ────────────────────────────────────────────────────────────

def run_analyste(state: CrisisState) -> CrisisState:
    """
    Classifie chaque tweet de l'échantillon par narratif et type d'acteur.

    Input  : state["tweets_sample"], state["corpus_config"]
    Output : state["narratives"] = NarrativeResult sérialisé
    """
    df: pd.DataFrame = state["tweets_sample"]
    config: dict = state.get("corpus_config", {})

    cols = ["postID", "message_normalizer", "Full Text", "Author",
            "X Verified", "X Followers", "Engagement Type"]
    sample = df[[c for c in cols if c in df.columns]].copy()

    evenement = config.get("evenement", "crise virale")
    periode   = config.get("periode", "")

    # LLM et prompt instanciés une seule fois, partagés entre tous les batches
    llm    = get_llm()
    parser = PydanticOutputParser(pydantic_object=BatchResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt("analyste")),
        ("human", (
            "Contexte événement : {evenement} — Période : {periode}\n\n"
            "Catégories de narratif (utilise EXACTEMENT ces libellés) : {narratifs}\n"
            "Catégories de type d'acteur : {acteurs}\n\n"
            "{few_shot}\n\n"
            "Tweets à classifier :\n\n{tweets}\n\n"
            "Retourne un TweetAnalysis par tweet (n'en invente pas d'autres). "
            "tweet_id = postID exact entre crochets. "
            "source_tweet_ids doit contenir au minimum le tweet_id lui-même.\n"
            "{format_instructions}"
        )),
    ])

    all_analyses: list[TweetAnalysis] = []
    errors: list[str] = list(state.get("errors", []))

    for start in range(0, len(sample), BATCH_SIZE):
        batch = sample.iloc[start:start + BATCH_SIZE]
        try:
            all_analyses.extend(
                _classify_batch(batch, evenement, periode, llm, prompt, parser)
            )
        except Exception as exc:
            errors.append(f"[analyste] batch {start}-{start + len(batch)} : {exc}")

    # Garde-fou : on ne garde que les tweet_id réellement présents dans l'échantillon
    valid_ids = set(sample["postID"].astype(str))
    all_analyses = [a for a in all_analyses if a.tweet_id in valid_ids]

    # Normalisation des labels hors taxonomie
    for a in all_analyses:
        if a.narratif not in NARRATIFS_VALIDES:
            a.narratif = "autre"
        if a.acteur_type not in ACTEURS_VALIDES:
            a.acteur_type = "anonyme"
        if not a.source_tweet_ids:
            a.source_tweet_ids = [a.tweet_id]

    # Agrégations calculées en Python — jamais laissées au LLM
    repartition       = dict(Counter(a.narratif for a in all_analyses))
    narratif_dominant = max(repartition, key=repartition.get) if repartition else "autre"

    state["narratives"] = NarrativeResult(
        analyses=all_analyses,
        narratif_dominant=narratif_dominant,
        repartition=repartition,
        source_tweet_ids=[a.tweet_id for a in all_analyses],
    ).model_dump()
    state["errors"] = errors
    return state
