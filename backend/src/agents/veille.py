from __future__ import annotations
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from prompts.prompts import get_system_prompt, get_llm
from pipeline.state import CrisisState
from tools.thresholds import compute_thresholds


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
#   → Synchronicité multi-comptes          ← signal d'orchestration
#   → Rapid-fire mono-compte               ← signal bot/scripté
#
# Signaux fiables mais rares (2-7% non-nuls) :
#   → Likes/Shares > 0 sont de VRAIS signaux viraux
#     (la plupart ont 0 par artefact de collecte — les non-nuls sont les tweets seeds)
#
# Signal de persistance (pas prédictif) :
#   → RT ratio > 90% SANS pic volume = crise qui dure, pas crise qui commence
#
# À ignorer :
#   → Impressions (6.7% non-nuls, unreliable)
#   → Reach (39.9% non-nuls, corrélé à Impressions, 20k doublons)
#   → Hashtags (95.7% vides)


def _compute_coordination_signals(df: pd.DataFrame, thresholds: dict) -> dict:
    """Calcule les signaux de coordination. Retourne un dict résumant les anomalies."""
    dates = pd.to_datetime(df["Date"])
    ts = df.assign(Date=dates).dropna(subset=["Date"])

    # Synchronicité : rafales multi-comptes (fenêtre 5 min)
    bins = pd.to_datetime(ts["Date"]).dt.floor("5min")
    distinct = ts.groupby(bins)["X Author ID"].nunique()
    sync_threshold = thresholds["SYNC_BURST_AUTHORS_THRESHOLD"]
    sync_bursts = distinct[distinct >= sync_threshold]

    # Rapid-fire : un même compte enchaîne posts en ≤ 60s
    rf = ts.sort_values(["X Author ID", "Date"]).copy()
    rf["_delta_s"] = (
        rf.groupby("X Author ID")["Date"].diff().dt.total_seconds()  # type: ignore[union-attr]
    )
    rapid_accounts = rf[rf["_delta_s"] <= 60]["X Author ID"].nunique()
    rf_threshold = thresholds["RAPID_FIRE_ACCOUNTS_THRESHOLD"]

    # Copy-paste inter-comptes (hors retweets)
    text_col = "message_normalizer" if "message_normalizer" in df.columns else "Full Text"
    cp = df[df["Engagement Type"] != "RETWEET"].copy()
    cp = cp[cp[text_col].str.len() >= 30]
    cp_clusters = 0
    if len(cp):
        cross = cp.groupby(text_col)["X Author ID"].nunique()
        cp_clusters = (cross >= 2).sum()

    return {
        "sync_burst_windows":     len(sync_bursts),
        "sync_burst_max_authors": int(sync_bursts.max()) if len(sync_bursts) else 0,
        "rapid_fire_accounts":    rapid_accounts,
        "copy_paste_clusters":    cp_clusters,
        "coordination_alert": (
            len(sync_bursts) > 0
            or rapid_accounts > rf_threshold
            or cp_clusters >= thresholds["COPY_PASTE_CLUSTERS_THRESHOLD"]
        ),
    }


def _compute_actor_signals(df: pd.DataFrame, thresholds: dict) -> dict:
    """Signaux d'alerte basés sur le profil des acteurs (influenceurs et comptes vérifiés)."""
    df = df.copy()
    verified_mask   = df["X Verified"].fillna(False).astype(bool)
    influencer_mask = ~verified_mask & (df["X Followers"].fillna(0) >= 10_000)

    # Signal 1 — Influencer burst (journalier)
    inf_df              = df[influencer_mask].dropna(subset=["Date"])
    inf_burst_days      = 0
    inf_burst_max_count = 0
    if len(inf_df) > 0:
        daily_inf  = inf_df.groupby(pd.to_datetime(inf_df["Date"]).dt.date)["X Author ID"].nunique()
        active     = daily_inf[daily_inf >= thresholds["INFLUENCER_BURST_N"]]
        inf_burst_days      = len(active)
        inf_burst_max_count = active.max() if len(active) else 0

    # Signal 2 — Verified sentiment cascade
    ver_df             = df[verified_mask].dropna(subset=["Date"])
    verified_neg_ratio = 0.0
    verified_neg_alert = False
    if len(ver_df) > 0:
        neg_ratio          = (ver_df["Sentiment"] == "negative").mean()
        verified_neg_ratio = round(neg_ratio, 3)
        verified_neg_alert = bool(neg_ratio >= thresholds["VERIFIED_NEG_THRESHOLD"])

    return {
        "influencer_burst_days":      inf_burst_days,
        "influencer_burst_max_count": inf_burst_max_count,
        "influencer_burst_alert":     inf_burst_days > 0,
        "verified_neg_ratio":         verified_neg_ratio,
        "verified_neg_alert":         verified_neg_alert,
        "actor_alert":                inf_burst_days > 0 or verified_neg_alert,
    }


def run_veille(state: CrisisState) -> CrisisState:
    df: pd.DataFrame = state["raw_df"].copy()

    # ── 0. Seuils dynamiques calibrés sur ce corpus (avec cache) ─────────────
    thresholds = compute_thresholds(df)

    VOLUME_ALERT_PER_DAY   = thresholds["VOLUME_ALERT_PER_DAY"]
    VIRAL_LIKES_THRESHOLD  = thresholds["VIRAL_LIKES_THRESHOLD"]
    VIRAL_SHARES_THRESHOLD = thresholds["VIRAL_SHARES_THRESHOLD"]
    RETWEET_RATIO_ALERT    = thresholds["RETWEET_RATIO_ALERT"]

    # ── 1. Volume horaire et journalier ───────────────────────────────────────
    dates = pd.to_datetime(df["Date"])
    df["_hour"] = dates.dt.floor("h")
    df["_day"]  = dates.dt.date

    hourly_vol = df.groupby("_hour").size().rename("count")
    daily_vol  = df.groupby("_day").size().rename("count")

    peak_days = daily_vol[daily_vol > VOLUME_ALERT_PER_DAY].sort_values(ascending=False)

    # ── 2. Tweets vraiment viraux (Likes ou Shares > seuil) ──────────────────
    viral_tweets = df[
        (df["Likes"] >= VIRAL_LIKES_THRESHOLD) |
        (df["Shares"] >= VIRAL_SHARES_THRESHOLD)
    ].sort_values("Shares", ascending=False)

    # ── 3. RT ratio journalier (signal de persistance, pas de prédiction) ────
    daily_rt = (
        df.groupby("_day")["Engagement Type"]
        .apply(lambda x: (x == "RETWEET").mean())
    )
    rt_persistence_days = daily_rt[
        (daily_rt > RETWEET_RATIO_ALERT) &
        ~daily_rt.index.isin(peak_days.index)
    ]

    # ── 4. Signaux de coordination ────────────────────────────────────────────
    coord_signals = _compute_coordination_signals(df, thresholds)

    # ── 4b. Signaux acteurs (influenceurs + vérifiés) ─────────────────────────
    actor_signals = _compute_actor_signals(df, thresholds)

    # ── 5. Sentiment par jour (évolution du ton) ──────────────────────────────
    sentiment_daily = (
        df.groupby(["_day", "Sentiment"])
        .size()
        .unstack(fill_value=0)
    )

    # ── 6. Détermination du niveau d'alerte ───────────────────────────────────
    vol_alert          = len(peak_days) > 0
    viral_alert        = len(viral_tweets) > 0
    coord_alert        = coord_signals["coordination_alert"]
    inf_burst_alert    = actor_signals["influencer_burst_alert"]
    verified_neg_alert = actor_signals["verified_neg_alert"]

    is_alert = vol_alert or viral_alert or coord_alert or inf_burst_alert or verified_neg_alert

    if vol_alert and (coord_alert or inf_burst_alert):
        forced_level = "critical"
    elif vol_alert or (viral_alert and (coord_alert or inf_burst_alert)):
        forced_level = "high"
    elif viral_alert or coord_alert or inf_burst_alert or verified_neg_alert:
        forced_level = "medium"
    else:
        forced_level = "low"

    # ── 7. Construction du résumé pour le LLM ────────────────────────────────
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

    coord_summary = (
        f"Coordination détectée : {coord_signals['sync_burst_windows']} fenêtres synchrones "
        f"(max {coord_signals['sync_burst_max_authors']} auteurs/5min), "
        f"{coord_signals['rapid_fire_accounts']} comptes rapid-fire, "
        f"{coord_signals['copy_paste_clusters']} clusters copy-paste inter-comptes."
        if coord_alert
        else "Pas de signal de coordination anormal détecté."
    )

    persistence_summary = (
        f"{len(rt_persistence_days)} jours avec RT ratio > {RETWEET_RATIO_ALERT:.0%} "
        f"hors pics de volume (crise persistante, pas de nouveau pic)."
        if len(rt_persistence_days) > 0
        else ""
    )

    actor_summary = ""
    if inf_burst_alert:
        actor_summary += (
            f"Burst d'influenceurs : {actor_signals['influencer_burst_days']} jour(s) "
            f"avec ≥ {thresholds['INFLUENCER_BURST_N']} influenceurs distincts "
            f"(max {actor_signals['influencer_burst_max_count']} auteurs/jour). "
        )
    if verified_neg_alert:
        actor_summary += (
            f"Cascade sentiment vérifiés : {actor_signals['verified_neg_ratio']:.0%} de tweets négatifs "
            f"parmi les comptes vérifiés (seuil : {thresholds['VERIFIED_NEG_THRESHOLD']:.0%})."
        )
    if not actor_summary:
        actor_summary = "Pas de signal acteur anormal (influenceurs ou comptes vérifiés)."

    # ── 8. LLM : génère uniquement le résumé textuel ─────────────────────────
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt("veille")),
        ("human", (
            "Voici les données de propagation calculées par pandas (ne pas inventer de chiffres) :\n\n"
            "Jours de pic (volume > {vol_threshold} tweets/j, seuil mean+2σ sur corpus) :\n{temporal_summary}\n\n"
            "Évolution du sentiment négatif :\n{sentiment_summary}\n\n"
            "Tweets vraiment viraux (Likes ≥ {likes_t} ou Shares ≥ {shares_t}) : {viral_count} tweets\n"
            "Leurs postIDs : {viral_ids}\n\n"
            "Signaux de coordination :\n{coord_summary}\n\n"
            "Signaux acteurs (influenceurs / vérifiés) :\n{actor_summary}\n\n"
            "Signal de persistance RT :\n{persistence_summary}\n\n"
            "À partir de ces données, génère un AlertSignal avec :\n"
            "- is_alert={is_alert}\n"
            "- alert_level={forced_level} (imposé par la logique de détection)\n"
            "- la liste des PeakEvent issus des données ci-dessus\n"
            "- un summary factuel de 2-3 phrases sur la dynamique de propagation, "
            "incluant les signaux de coordination si présents"
        )),
    ])

    result: AlertSignal = (prompt | llm.with_structured_output(AlertSignal)).invoke({  # type: ignore[assignment]
        "vol_threshold":       VOLUME_ALERT_PER_DAY,
        "temporal_summary":    temporal_summary,
        "sentiment_summary":   sentiment_summary,
        "likes_t":             VIRAL_LIKES_THRESHOLD,
        "shares_t":            VIRAL_SHARES_THRESHOLD,
        "viral_count":         len(viral_tweets),
        "viral_ids":           str(viral_ids),
        "coord_summary":       coord_summary,
        "actor_summary":       actor_summary,
        "persistence_summary": persistence_summary,
        "is_alert":            is_alert,
        "forced_level":        forced_level,
    })

    # Override des champs calculés par pandas (ne jamais laisser le LLM inventer des chiffres)
    result.is_alert    = is_alert
    result.alert_level = forced_level
    result.threshold_breaches = {
        "peak_days_count":              len(peak_days),
        "viral_tweets_count":           len(viral_tweets),
        "max_daily_volume":             daily_vol.max(),
        "max_hourly_volume":            hourly_vol.max(),
        "coordination_alert":           coord_alert,
        "sync_burst_windows":           coord_signals["sync_burst_windows"],
        "rapid_fire_accounts":          coord_signals["rapid_fire_accounts"],
        "copy_paste_clusters":          coord_signals["copy_paste_clusters"],
        "influencer_burst_alert":     inf_burst_alert,
        "influencer_burst_days":      actor_signals["influencer_burst_days"],
        "influencer_burst_max_count": actor_signals["influencer_burst_max_count"],
        "verified_neg_alert":           verified_neg_alert,
        "verified_neg_ratio":           actor_signals["verified_neg_ratio"],
        "rt_persistence_days":          len(rt_persistence_days),
        "thresholds_granularity":       thresholds["_corpus_stats"]["granularity"],
    }

    state["alerts"] = result.model_dump()
    return state
