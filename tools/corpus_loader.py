from __future__ import annotations
import pandas as pd


def load_corpus(path: str = "Dataset/data.xlsx") -> pd.DataFrame:
    """
    Charge et nettoie data.xlsx.
    Retourne un DataFrame propre — seule fonction autorisée à lire le fichier.

    Corpus : 35 396 tweets, 100% français, 19 mars → 1er mai 2026. ~95 Mo en RAM.

    Notes sur la qualité des données :
    - Likes/Shares/Comments : 93-98% à zéro (artefact de collecte, pas engagement réel).
      Les tweets avec valeur > 0 sont les vrais viraux — les garder comme signal rare.
    - Impressions : seulement 6.7% non-nuls. À ignorer.
    - Reach : 39.9% non-nuls mais corrélé à 0.80 avec Impressions + 20k doublons.
      À ignorer pour l'analyse.
    - Le signal principal de crise = VOLUME (nombre de tweets/heure), pas l'engagement
      individuel. Chaque ligne = un acte de diffusion.
    - Hashtags : 95.7% vides (limiter leur usage en analyse).
    - City/City Code : 50.6% vides (analyse géographique limitée).
    """
    df = pd.read_excel(path, engine="openpyxl")

    # Dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["postDate"] = pd.to_datetime(df["postDate"], errors="coerce")

    # IDs en str (ne pas caster en int — risque de troncature)
    for col in ["postID", "X Author ID"]:
        df[col] = df[col].astype(str)

    # Booléen
    df["X Verified"] = df["X Verified"].fillna(False).astype(bool)

    # Numériques
    for col in ["Likes", "Comments", "Shares", "Impressions", "Reach",
                "X Followers", "X Following", "X Posts"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Texte
    for col in ["Full Text", "message_normalizer", "Hashtags", "Author",
                "Mentioned Authors", "Expanded URLs"]:
        df[col] = df[col].fillna("").astype(str)

    # Engagement Type : NaN = tweet original
    df["Engagement Type"] = df["Engagement Type"].fillna("ORIGINAL").astype(str)

    # Sentiment et Language
    df["Sentiment"] = df["Sentiment"].fillna("neutral").astype(str)
    df["Language"] = df["Language"].fillna("fr").astype(str)

    # Doublons (aucun dans le corpus actuel, par précaution)
    df = df.drop_duplicates(subset=["postID"])

    # Tri chronologique
    df = df.sort_values("Date").reset_index(drop=True)

    print(
        f"[load_corpus] {len(df):,} tweets | "
        f"{df['Date'].min().date()} → {df['Date'].max().date()} | "
        f"RETWEET={len(df[df['Engagement Type']=='RETWEET']):,} "
        f"REPLY={len(df[df['Engagement Type']=='REPLY']):,} "
        f"QUOTE={len(df[df['Engagement Type']=='QUOTE']):,}"
    )
    return df
