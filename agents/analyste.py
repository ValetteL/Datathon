from __future__ import annotations
from collections import Counter
import pandas as pd
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from prompts.prompts import get_system_prompt, get_llm
from pipeline.state import CrisisState


# ── Schémas Pydantic (AD-4 : outputs typés, AD-10 : source_tweet_ids obligatoire) ──

class TweetAnalysis(BaseModel):
    tweet_id: str = Field(description="postID du tweet analysé")
    narratif: str = Field(
        description="censure | copinage | defense_ultia | defense_cnc | autre"
    )
    acteur_type: str = Field(
        description="media | militant | influenceur | anonyme | institution"
    )
    source_tweet_ids: list[str] = Field(
        description="Liste des postID cités comme sources (au minimum le tweet_id lui-même)"
    )


class NarrativeResult(BaseModel):
    analyses: list[TweetAnalysis]
    narratif_dominant: str = Field(description="Le narratif le plus fréquent dans l'échantillon")
    repartition: dict = Field(description="Comptage par catégorie de narratif")
    source_tweet_ids: list[str] = Field(description="Tous les postID analysés")


# ── Taxonomie de référence (alimentée par l'exploration manuelle Story 1.3 — P2) ──
# Catégories figées pour éviter la dérive du LLM sur des labels libres.
NARRATIFS_VALIDES = ["censure", "copinage", "defense_ultia", "defense_cnc", "autre"]
ACTEURS_VALIDES = ["media", "militant", "influenceur", "anonyme", "institution"]

# Few-shot minimal (AD-9 : pas de hardcode métier dans la logique, seulement dans
# les exemples qui calibrent la classification — à enrichir avec les vrais
# exemples remontés par P2 en Story 1.3).
FEW_SHOT_EXAMPLES = """Exemples de calibration (à titre indicatif, ne pas recopier littéralement) :
- "Ils censurent encore une fois la vérité, c'est inadmissible" → narratif=censure, acteur_type=militant
- "Tout le monde savait, c'est encore un copinage entre les mêmes personnes" → narratif=copinage, acteur_type=anonyme
- "Le CNC applique simplement le règlement, rien d'anormal ici" → narratif=defense_cnc, acteur_type=institution
- "Ultia n'a rien fait de mal, on s'acharne sur eux sans preuve" → narratif=defense_ultia, acteur_type=influenceur
- "Je n'ai pas d'avis tranché, attendons d'en savoir plus" → narratif=autre, acteur_type=anonyme"""

BATCH_SIZE = 200  # taille de batch envoyée au LLM par appel (limite tokens/contexte)


def _format_tweets(sample: pd.DataFrame) -> str:
    """Formate un sous-ensemble de tweets en texte lisible pour le prompt."""
    lines = []
    for _, row in sample.iterrows():
        text = row.get("message_normalizer") or row.get("Full Text") or ""
        lines.append(
            f"[{row['postID']}] @{row['Author']} "
            f"(followers:{row['X Followers']}, verified:{row['X Verified']}, "
            f"type:{row['Engagement Type']})\n{text}"
        )
    return "\n\n".join(lines)


def _classify_batch(
    sample: pd.DataFrame,
    evenement: str,
    periode: str,
) -> list[TweetAnalysis]:
    """Classifie un batch de tweets via le LLM et retourne la liste des analyses."""
    if sample.empty:
        return []

    tweets_text = _format_tweets(sample)
    parser = PydanticOutputParser(pydantic_object=NarrativeResult)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt("analyste")),
        ("human", (
            "Contexte événement : {evenement} — Période : {periode}\n\n"
            "Catégories de narratif autorisées (utilise EXACTEMENT ces libellés) : "
            "{narratifs}\n"
            "Catégories de type d'acteur autorisées : {acteurs}\n\n"
            "{few_shot}\n\n"
            "Voici un échantillon de tweets à classifier :\n\n{tweets}\n\n"
            "Pour chaque tweet listé ci-dessus (un seul TweetAnalysis par tweet, "
            "n'en invente pas d'autres), identifie le narratif et le type d'acteur. "
            "tweet_id doit correspondre exactement au postID entre crochets. "
            "source_tweet_ids doit au minimum contenir le tweet_id lui-même.\n"
            "{format_instructions}"
        )),
    ])

    chain = prompt | llm | parser

    result: NarrativeResult = chain.invoke({
        "evenement": evenement,
        "periode": periode,
        "narratifs": ", ".join(NARRATIFS_VALIDES),
        "acteurs": ", ".join(ACTEURS_VALIDES),
        "few_shot": FEW_SHOT_EXAMPLES,
        "tweets": tweets_text,
        "format_instructions": parser.get_format_instructions(),
    })

    return result.analyses


def run_analyste(state: CrisisState) -> CrisisState:
    """
    Nœud AgentAnalyste — classifie chaque tweet de l'échantillon selon son
    narratif dominant et le type d'acteur qui le produit.

    Input  : state["tweets_sample"], state["corpus_config"]
    Output : state["narratives"] = NarrativeResult sérialisé (dict)
    """
    df: pd.DataFrame = state["tweets_sample"]
    config: dict = state.get("corpus_config", {})

    cols = ["postID", "message_normalizer", "Full Text", "Author",
            "X Verified", "X Followers", "Engagement Type"]
    cols = [c for c in cols if c in df.columns]
    sample = df[cols].copy()

    evenement = config.get("evenement", "crise virale")
    periode = config.get("periode", "")

    all_analyses: list[TweetAnalysis] = []
    errors: list[str] = list(state.get("errors", []))

    for start in range(0, len(sample), BATCH_SIZE):
        batch = sample.iloc[start:start + BATCH_SIZE]
        try:
            all_analyses.extend(_classify_batch(batch, evenement, periode))
        except Exception as exc:  # noqa: BLE001 — on isole l'erreur par batch
            errors.append(f"[analyste] batch {start}-{start + len(batch)} : {exc}")

    # Garde-fou anti-hallucination (AD-10) : on ne garde que les analyses dont
    # le tweet_id correspond à un postID réellement présent dans l'échantillon.
    valid_ids = set(sample["postID"].astype(str))
    all_analyses = [a for a in all_analyses if a.tweet_id in valid_ids]

    # Normalisation des catégories hors taxonomie -> "autre" / "anonyme"
    for a in all_analyses:
        if a.narratif not in NARRATIFS_VALIDES:
            a.narratif = "autre"
        if a.acteur_type not in ACTEURS_VALIDES:
            a.acteur_type = "anonyme"
        if not a.source_tweet_ids:
            a.source_tweet_ids = [a.tweet_id]

    repartition = dict(Counter(a.narratif for a in all_analyses))
    narratif_dominant = max(repartition, key=repartition.get) if repartition else "autre"
    source_tweet_ids = [a.tweet_id for a in all_analyses]

    result = NarrativeResult(
        analyses=all_analyses,
        narratif_dominant=narratif_dominant,
        repartition=repartition,
        source_tweet_ids=source_tweet_ids,
    )

    state["narratives"] = result.model_dump()
    state["errors"] = errors
    return state
