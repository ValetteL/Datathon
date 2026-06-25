from __future__ import annotations
import pandas as pd
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from prompts.prompts import get_system_prompt, get_llm
from pipeline.state import CrisisState


class PeakEvent(BaseModel):
    date: str = Field(description="Date du pic (YYYY-MM-DD)")
    tweet_count: int = Field(description="Nombre de tweets ce jour-là")
    top_shares: int = Field(description="Valeur max de Shares ce jour-là")
    source_tweet_ids: list[str] = Field(description="postIDs des tweets les plus partagés")


class AlertSignal(BaseModel):
    is_alert: bool
    alert_level: str = Field(description="low | medium | high | critical")
    peaks: list[PeakEvent]
    threshold_breaches: dict = Field(description="Métriques et valeurs ayant dépassé les seuils")
    summary: str = Field(description="Synthèse factuelle de la dynamique de propagation")
    source_tweet_ids: list[str]


# ── Stratégie de détection — comprendre avant de seuiller ────────────────────
#
# Ce corpus est un corpus de DIFFUSION, pas d'engagement.
# Chaque ligne = un acte de diffusion (retweet, reply, quote, ou post original).
#
# Signaux fiables (100% couverts) :
#   → Volume de tweets par heure/jour      ← signal principal de crise
#   → Engagement Type (RETWEET/REPLY/QUOTE/ORIGINAL) ← vitesse d'amplification
#   → Sentiment par plage horaire          ← montée en agressivité
#
# Signaux fiables mais rares (2-7% non-nuls) :
#   → Likes/Shares/Comments > 0 sont de VRAIS signaux viraux
#     (la plupart ont 0 par artefact de collecte — les non-nuls sont les tweets seeds)
#
# À ignorer :
#   → Impressions (6.7% non-nuls, unreliable)
#   → Reach (39.9% non-nuls, corrélé à Impressions, 20k doublons)
#   → Hashtags (95.7% vides)

VOLUME_ALERT_PER_HOUR = 300    # ~2% des heures dépassent ce seuil sur le corpus
VOLUME_ALERT_PER_DAY  = 2_000  # pic observé : 7 303 le 27 mars
RETWEET_RATIO_ALERT   = 0.90   # >90% de RT = phase d'amplification massive
VIRAL_LIKES_THRESHOLD = 50     # un tweet avec >50 likes dans ce corpus est vraiment viral
VIRAL_SHARES_THRESHOLD = 20    # idem pour les shares


def run_veille(state: CrisisState) -> CrisisState:
    df: pd.DataFrame = state["raw_df"].copy()

    # ── 1. Volume horaire et journalier ───────────────────────────────────────
    df["_hour"] = df["Date"].dt.floor("h")
    df["_day"]  = df["Date"].dt.date

    hourly_vol = df.groupby("_hour").size().rename("count")
    daily_vol  = df.groupby("_day").size().rename("count")

    peak_days  = daily_vol[daily_vol > VOLUME_ALERT_PER_DAY].sort_values(ascending=False)

    # ── 2. Tweets vraiment viraux (Likes ou Shares > seuil) ──────────────────
    viral_tweets = df[
        (df["Likes"] >= VIRAL_LIKES_THRESHOLD) |
        (df["Shares"] >= VIRAL_SHARES_THRESHOLD)
    ].sort_values("Shares", ascending=False)

    # ── 4. Sentiment par jour (évolution du ton) ──────────────────────────────
    sentiment_daily = (
        df.groupby(["_day", "Sentiment"])
        .size()
        .unstack(fill_value=0)
    )

    # ── 5. Construction du résumé pour le LLM ─────────────────────────────────
    is_alert = len(peak_days) > 0 or len(viral_tweets) > 0

    peak_events_data = []
    for day in list(peak_days.index)[:5]:
        day_df = df[df["_day"] == day]
        top_viral = day_df.nlargest(3, "Shares")
        peak_events_data.append({
            "date": str(day),
            "tweet_count": int(daily_vol[day]),
            "retweet_ratio": round(float((day_df["Engagement Type"] == "RETWEET").mean()), 2),
            "source_tweet_ids": top_viral["postID"].tolist(),
        })

    viral_ids = viral_tweets["postID"].head(10).tolist()

    temporal_summary = "\n".join(
        f"{e['date']}: {e['tweet_count']} tweets, RT ratio={e['retweet_ratio']:.0%}"
        for e in peak_events_data
    )

    sentiment_summary = ""
    if not sentiment_daily.empty and "negative" in sentiment_daily.columns:
        neg_trend = sentiment_daily["negative"].to_dict()
        sentiment_summary = "Tweets négatifs/jour : " + ", ".join(
            f"{str(d)}: {v}" for d, v in list(neg_trend.items())[:7]
        )

    # ── 6. LLM : génère uniquement le résumé textuel ─────────────────────────
    parser = PydanticOutputParser(pydantic_object=AlertSignal)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt("veille")),
        ("human", (
            "Voici les données de propagation calculées par pandas (ne pas inventer de chiffres) :\n\n"
            "Jours de pic (volume > {vol_threshold} tweets/j) :\n{temporal_summary}\n\n"
            "Évolution du sentiment négatif :\n{sentiment_summary}\n\n"
            "Tweets vraiement viraux (Likes ≥ {likes_t} ou Shares ≥ {shares_t}) : {viral_count} tweets\n"
            "Leurs postIDs : {viral_ids}\n\n"
            "À partir de ces données, génère un AlertSignal avec :\n"
            "- is_alert={is_alert}\n"
            "- alert_level adapté à l'intensité (low/medium/high/critical)\n"
            "- la liste des PeakEvent issus des données ci-dessus\n"
            "- un summary factuel de 2-3 phrases sur la dynamique de propagation\n"
            "{format_instructions}"
        )),
    ])

    chain = prompt | llm | parser

    result: AlertSignal = chain.invoke({
        "vol_threshold": VOLUME_ALERT_PER_DAY,
        "temporal_summary": temporal_summary,
        "sentiment_summary": sentiment_summary,
        "likes_t": VIRAL_LIKES_THRESHOLD,
        "shares_t": VIRAL_SHARES_THRESHOLD,
        "viral_count": len(viral_tweets),
        "viral_ids": str(viral_ids),
        "is_alert": is_alert,
        "format_instructions": parser.get_format_instructions(),
    })

    # Override des champs calculés par pandas (ne jamais laisser le LLM inventer des chiffres)
    result.is_alert = is_alert
    result.threshold_breaches = {
        "peak_days_count": len(peak_days),
        "viral_tweets_count": len(viral_tweets),
        "max_daily_volume": int(daily_vol.max()),
        "max_hourly_volume": int(hourly_vol.max()),
    }

    state["alerts"] = result.model_dump()
    return state
