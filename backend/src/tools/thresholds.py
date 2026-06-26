"""
Calcul et mise en cache des seuils dynamiques pour l'agent veille.

Chaque appel à compute_thresholds() retourne un dict de seuils calibrés sur le
corpus fourni. Le résultat est écrit dans outputs/thresholds_<hash>.json et rechargé
automatiquement tant que le corpus n'a pas changé.

Granularité auto-sélectionnée :
  ≤ 60 jours  → daily   : mean+2σ sur volumes journaliers
  ≤ 180 jours → weekly  : baseline = volume hebdo / 7
  > 180 jours → monthly : baseline = volume mensuel / 30

Usage :
    from tools.thresholds import compute_thresholds
    t = compute_thresholds(df)
    t["VOLUME_ALERT_PER_DAY"]  # int, calibré sur CE corpus
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"


# ── Fingerprint ───────────────────────────────────────────────────────────────

def _dataset_hash(df: pd.DataFrame) -> str:
    key = f"{len(df)}-{df['Date'].min().isoformat()}-{df['Date'].max().isoformat()}"
    return hashlib.md5(key.encode()).hexdigest()[:10]


def _choose_granularity(span_days: int) -> str:
    if span_days <= 60:
        return "daily"
    if span_days <= 180:
        return "weekly"
    return "monthly"


# ── Sous-calculs ──────────────────────────────────────────────────────────────

def _volume_thresholds(df: pd.DataFrame, granularity: str) -> dict:
    df = df.copy()
    dates = pd.to_datetime(df["Date"])
    df["_hour"] = dates.dt.floor("h")
    df["_day"]  = dates.dt.date

    hourly_vol = df.groupby("_hour").size()
    daily_vol  = df.groupby("_day").size()

    if granularity == "weekly":
        df["_week"] = dates.dt.to_period("W")
        baseline_vols = df.groupby("_week").size() / 7.0
    elif granularity == "monthly":
        df["_month"] = dates.dt.to_period("M")
        baseline_vols = df.groupby("_month").size() / 30.0
    else:
        baseline_vols = daily_vol.astype(float)

    vol_mean = baseline_vols.mean()
    vol_std  = baseline_vols.std()

    return {
        "VOLUME_ALERT_PER_DAY":  int(vol_mean + 2 * vol_std),
        "VOLUME_ALERT_PER_HOUR": int(hourly_vol.mean() + 2 * hourly_vol.std()),
        "_vol_stats": {
            "granularity":   granularity,
            "daily_mean":    round(daily_vol.mean(), 1),
            "daily_std":     round(daily_vol.std(), 1),
            "baseline_mean": round(vol_mean, 1),
            "baseline_std":  round(vol_std, 1),
        },
    }


def _viral_thresholds(df: pd.DataFrame) -> dict:
    likes_nz  = df[df["Likes"]  > 0]["Likes"]
    shares_nz = df[df["Shares"] > 0]["Shares"]
    return {
        "VIRAL_LIKES_THRESHOLD":  int(likes_nz.quantile(0.90))  if len(likes_nz)  else 50,
        "VIRAL_SHARES_THRESHOLD": int(shares_nz.quantile(0.75)) if len(shares_nz) else 20,
        "_viral_stats": {
            "likes_nonzero_pct":  round(len(likes_nz)  / len(df), 3),
            "shares_nonzero_pct": round(len(shares_nz) / len(df), 3),
        },
    }


def _rt_thresholds(df: pd.DataFrame) -> dict:
    daily_rt = (
        df.groupby(pd.to_datetime(df["Date"]).dt.date)["Engagement Type"]
        .apply(lambda x: (x == "RETWEET").mean())
    )
    return {
        "RETWEET_RATIO_ALERT":       0.90,
        "RETWEET_PERSISTENCE_ALERT": 0.90,
        "_rt_stats": {
            "rt_ratio_mean":   round(daily_rt.mean(),   3),
            "rt_ratio_median": round(daily_rt.median(), 3),
        },
    }


def _actor_thresholds(df: pd.DataFrame) -> dict:
    """
    Seuils basés sur le profil des acteurs.

    - Influencer burst   : p90 d'influenceurs distincts par jour (min 2)
    - Verified sentiment : mean + 1.5σ du ratio négatif journalier des vérifiés, plafonné à 0.70
    """
    df = df.copy()
    verified_mask   = df["X Verified"].fillna(False).astype(bool)
    influencer_mask = ~verified_mask & (df["X Followers"].fillna(0) >= 10_000)

    # --- Influencer burst (journalier — plus stable que 30min sur corpus peu dense)
    inf_df = df[influencer_mask].dropna(subset=["Date"])
    if len(inf_df) > 0:
        daily_inf   = inf_df.groupby(pd.to_datetime(inf_df["Date"]).dt.date)["X Author ID"].nunique()
        inf_burst_n = max(2, int(daily_inf.quantile(0.90)))
    else:
        inf_burst_n = 2

    # --- Verified sentiment cascade
    ver_df = df[verified_mask].dropna(subset=["Date"])
    v_mean = 0.0
    v_std  = 0.0
    if len(ver_df) > 0:
        daily_neg = (
            ver_df.groupby(pd.to_datetime(ver_df["Date"]).dt.date)["Sentiment"]
            .apply(lambda x: (x == "negative").mean())
        )
        v_mean = daily_neg.mean()
        v_std  = daily_neg.std()
        verified_neg_threshold = min(0.70, round(v_mean + 1.5 * v_std, 3))
    else:
        verified_neg_threshold = 0.40

    return {
        "INFLUENCER_BURST_N":     inf_burst_n,
        "VERIFIED_NEG_THRESHOLD": verified_neg_threshold,
        "_actor_stats": {
            "n_influencer_tweets": influencer_mask.sum(),
            "n_verified_tweets":   verified_mask.sum(),
            "verified_neg_mean":   round(v_mean, 3),
            "verified_neg_std":    round(v_std, 3),
        },
    }


def _coordination_thresholds(df: pd.DataFrame) -> dict:
    """
    Seuils auto-calibrés à partir du corpus.

    - Synchronicité : p95 d'auteurs distincts par fenêtre 5 min
    - Rapid-fire    : alarme si > 1 % des auteurs uniques sont rapid-fire
    - Copy-paste    : alarme dès 1 cluster inter-comptes (> 2 comptes même texte)
    - Comptes récents : p10 de X Posts comme proxy pour "compte peu actif"
    """
    ts = df.dropna(subset=["Date"])

    # --- synchronicité
    bins = pd.to_datetime(ts["Date"]).dt.floor("5min")
    distinct = ts.groupby(bins)["X Author ID"].nunique()
    sync_threshold = int(distinct.quantile(0.95))

    # --- rapid-fire
    rf = ts.sort_values(["X Author ID", "Date"]).copy()
    rf["_delta_s"] = (
        rf.groupby("X Author ID")["Date"]
        .transform(lambda x: pd.to_datetime(x).diff().dt.total_seconds())
    )
    rapid_accounts_observed = rf[rf["_delta_s"] <= 60]["X Author ID"].nunique()
    rf_threshold = max(1, int(ts["X Author ID"].nunique() * 0.01))

    # --- copy-paste (hors retweets)
    text_col = "message_normalizer" if "message_normalizer" in df.columns else "Full Text"
    cp = df[df["Engagement Type"] != "RETWEET"].copy()
    cp = cp[cp[text_col].str.len() >= 30]
    if len(cp):
        cross = cp.groupby(text_col)["X Author ID"].nunique()
        cp_clusters_observed = (cross >= 2).sum()
    else:
        cp_clusters_observed = 0

    # --- comptes récents
    recent_proxy = int(df["X Posts"].quantile(0.10)) if "X Posts" in df.columns else 100

    return {
        "SYNC_BURST_AUTHORS_THRESHOLD":    sync_threshold,
        "RAPID_FIRE_ACCOUNTS_THRESHOLD":   rf_threshold,
        "COPY_PASTE_CLUSTERS_THRESHOLD":   1,
        "RECENT_ACCOUNTS_POSTS_THRESHOLD": recent_proxy,
        "_coordination_stats": {
            "sync_p95_authors":             sync_threshold,
            "rapid_fire_accounts_observed": rapid_accounts_observed,
            "copy_paste_clusters_observed": cp_clusters_observed,
            "recent_account_proxy_posts":   recent_proxy,
        },
    }


# ── Point d'entrée public ─────────────────────────────────────────────────────

def compute_thresholds(
    df: pd.DataFrame,
    cache_dir: Path | None = None,
    force: bool = False,
) -> dict:
    """
    Retourne les seuils calibrés sur df. Résultat mis en cache par empreinte dataset.

    Args:
        df        : corpus complet chargé via load_corpus()
        cache_dir : répertoire de cache (défaut : backend/outputs/)
        force     : forcer le recalcul même si un cache existe
    Returns:
        dict de seuils + _corpus_stats
    """
    if cache_dir is None:
        cache_dir = _CACHE_DIR

    dh         = _dataset_hash(df)
    cache_path = cache_dir / f"thresholds_{dh}.json"

    if not force and cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            cached = json.load(f)
        if cached.get("_corpus_stats", {}).get("dataset_hash") == dh:
            return cached

    span_days   = (df["Date"].max() - df["Date"].min()).days
    granularity = _choose_granularity(span_days)

    thresholds: dict = {}
    thresholds.update(_volume_thresholds(df, granularity))
    thresholds.update(_viral_thresholds(df))
    thresholds.update(_rt_thresholds(df))
    thresholds.update(_coordination_thresholds(df))
    thresholds.update(_actor_thresholds(df))
    thresholds["_corpus_stats"] = {
        "dataset_hash": dh,
        "n_tweets":     len(df),
        "date_from":    str(df["Date"].min().date()),
        "date_to":      str(df["Date"].max().date()),
        "span_days":    span_days,
        "granularity":  granularity,
    }

    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2, ensure_ascii=False)

    return thresholds
