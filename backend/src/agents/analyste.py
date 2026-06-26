from __future__ import annotations
from collections import Counter
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.prompts.prompts import get_system_prompt, get_llm
from src.pipeline.state import CrisisState


# ── Schémas Pydantic ──────────────────────────────────────────────────────────


class TweetAnalysis(BaseModel):
    tweet_id: str = Field(description="postID du tweet analysé")
    narratif: str = Field(description="Catégorie de narratif dominant du tweet")
    acteur_type: str = Field(description="Type d'acteur ayant émis le tweet")
    source_tweet_ids: list[str] = Field(
        description="Liste des postID cités comme sources (au minimum le tweet_id lui-même)"
    )


class BatchResult(BaseModel):
    """Schema minimal envoyé au LLM — uniquement ce qu'il doit produire.
    Les champs agrégés (narratif_dominant, repartition) sont calculés en Python."""

    analyses: list[TweetAnalysis]


class NarrativeResult(BaseModel):
    analyses: list[TweetAnalysis]
    narratif_dominant: str = Field(
        description="Le narratif le plus fréquent dans l'échantillon"
    )
    repartition: dict = Field(description="Comptage par catégorie de narratif")
    source_tweet_ids: list[str] = Field(description="Tous les postID analysés")


# ── Taxonomie par défaut (générique — à surcharger via corpus_config) ─────────

DEFAULT_NARRATIFS = ["positif", "negatif", "neutre", "autre"]
DEFAULT_ACTEURS   = ["media", "militant", "influenceur", "anonyme", "institution", "coordonne_bot"]

DEFAULT_FEW_SHOT = """Exemples de calibration (adapter au contexte) :
- "C'est un scandale, ils ont menti depuis le début" → narratif=negatif, acteur_type=militant
- "Je suis fier de les soutenir, continuez !" → narratif=positif, acteur_type=anonyme
- "Voici les faits selon [source]" → narratif=neutre, acteur_type=media
- Compte postant 40 fois en 10 min avec textes identiques → acteur_type=coordonne_bot"""

BATCH_SIZE = 25


# ── Helpers ───────────────────────────────────────────────────────────────────


def _stratified_sample(df: pd.DataFrame, n: int = 300, random_state: int = 42) -> pd.DataFrame:
    """Equal-allocation stratified sample by Engagement Type.
    Works for any corpus regardless of type distribution."""
    types = [t for t in df["Engagement Type"].dropna().unique() if pd.notna(t)]
    if not types:
        return df.sample(min(n, len(df)), random_state=random_state)
    per_type = max(20, n // len(types))
    parts = []
    for etype in types:
        sub = df[df["Engagement Type"] == etype]
        if len(sub) > 0:
            parts.append(sub.sample(min(per_type, len(sub)), random_state=random_state))
    combined = pd.concat(parts)
    return combined.sample(frac=1, random_state=random_state).reset_index(drop=True)


def _format_tweets(batch: pd.DataFrame) -> str:
    lines = []
    for _, row in batch.iterrows():
        text = (row.get("message_normalizer") or row.get("Full Text") or "")[:200]
        followers = int(row.get("X Followers") or 0)
        lines.append(
            f"[{row['postID']}] {row['Engagement Type']}|v:{row['X Verified']}|f:{followers}|{text}"
        )
    return "\n".join(lines)


def _classify_batch(
    batch: pd.DataFrame,
    evenement: str,
    periode: str,
    narratifs: list[str],
    acteurs: list[str],
    few_shot: str,
    chain,
) -> list[TweetAnalysis]:
    if batch.empty:
        return []
    result: BatchResult = chain.invoke(
        {
            "evenement":  evenement,
            "periode":    periode,
            "narratifs":  ", ".join(narratifs),
            "acteurs":    ", ".join(acteurs),
            "few_shot":   few_shot,
            "tweets":     _format_tweets(batch),
        }
    )
    return result.analyses


# ── Nœud principal ────────────────────────────────────────────────────────────


def run_analyste(state: CrisisState) -> CrisisState:
    """
    Classifie chaque tweet par narratif et type d'acteur.

    Taxonomies et few-shot injectés via corpus_config — aucun label hardcodé.

    Input  : state["raw_df"], state["corpus_config"]
    Output : state["narratives"] = NarrativeResult sérialisé
    """
    config: dict = state.get("corpus_config", {})

    narratifs_valides: list[str] = config.get("narratifs", DEFAULT_NARRATIFS)
    acteurs_valides:   list[str] = config.get("acteurs",   DEFAULT_ACTEURS)
    few_shot:          str       = config.get("few_shot",  DEFAULT_FEW_SHOT)
    evenement:         str       = config.get("evenement", "crise virale")
    periode:           str       = config.get("periode",   "")

    cols = [
        "postID", "message_normalizer", "Full Text",
        "Author", "X Verified", "X Followers", "Engagement Type",
    ]
    raw    = state["raw_df"][[c for c in cols if c in state["raw_df"].columns]].copy()
    sample = _stratified_sample(raw, n=config.get("sample_size", 300))

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt("analyste")),
        ("human", (
            "Contexte événement : {evenement} — Période : {periode}\n\n"
            "Catégories de narratif (utilise EXACTEMENT ces libellés) : {narratifs}\n"
            "Catégories de type d'acteur (utilise EXACTEMENT ces libellés) : {acteurs}\n\n"
            "{few_shot}\n\n"
            "Tweets à classifier (format: [postID] TYPE|v:VERIFIED|f:FOLLOWERS|texte) :\n{tweets}\n\n"
            "Retourne un TweetAnalysis par tweet (n'en invente pas d'autres). "
            "tweet_id = postID exact entre crochets. "
            "source_tweet_ids doit contenir au minimum le tweet_id lui-même."
        )),
    ])
    chain = prompt | llm.with_structured_output(BatchResult)

    all_analyses: list[TweetAnalysis] = []
    errors: list[str] = list(state.get("errors", []))

    for start in range(0, len(sample), BATCH_SIZE):
        batch = sample.iloc[start : start + BATCH_SIZE]
        try:
            all_analyses.extend(
                _classify_batch(batch, evenement, periode, narratifs_valides, acteurs_valides, few_shot, chain)
            )
        except Exception as exc:
            errors.append(f"[analyste] batch {start}-{start + len(batch)} : {exc}")

    # Garde-fou : on ne garde que les tweet_id réellement présents dans l'échantillon
    valid_ids = set(sample["postID"].astype(str))
    all_analyses = [a for a in all_analyses if a.tweet_id in valid_ids]

    # Normalisation : fallback si le LLM sort un label hors taxonomie
    fallback_narratif = narratifs_valides[-1]  # dernier = "autre" par convention
    fallback_acteur   = "anonyme" if "anonyme" in acteurs_valides else acteurs_valides[-1]
    for a in all_analyses:
        if a.narratif not in narratifs_valides:
            a.narratif = fallback_narratif
        if a.acteur_type not in acteurs_valides:
            a.acteur_type = fallback_acteur
        if not a.source_tweet_ids:
            a.source_tweet_ids = [a.tweet_id]

    # Agrégations calculées en Python — jamais laissées au LLM
    repartition = dict(Counter(a.narratif for a in all_analyses))
    narratif_dominant = max(repartition, key=lambda k: repartition[k]) if repartition else fallback_narratif

    state["narratives"] = NarrativeResult(
        analyses=all_analyses,
        narratif_dominant=narratif_dominant,
        repartition=repartition,
        source_tweet_ids=[a.tweet_id for a in all_analyses],
    ).model_dump()
    state["errors"] = errors
    return state
