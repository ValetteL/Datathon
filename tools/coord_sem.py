import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tools.corpus_loader import load_corpus

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "coord_sem"

# message_normalizer ne porte que la date (pas l'heure) -> on retombe sur Date pour
# tout ce qui demande de la granularité temporelle (synchronicité, rapid-fire).

FRENCH_STOPWORDS = {
	"a", "abord", "afin", "ai", "ainsi", "alors", "am", "amp", "an", "ans", "apres",
	"au", "aucun", "aucune", "aujourd", "aupres", "aura", "aussi", "autre", "autres",
	"avaient", "avait", "avant", "avec", "avoir", "ayant", "b", "bien", "c", "ca",
	"car", "ce", "cela", "celle", "celles", "celui", "ces", "cet", "cette", "ceux",
	"chaque", "chez", "ci", "co", "comme", "comment", "contre", "d", "dans", "de",
	"deja", "depuis", "des", "deux", "devra", "doit", "donc", "dont", "du", "elle",
	"elles", "en", "encore", "entre", "es", "est", "et", "etaient", "etait", "etant",
	"ete", "etre", "eu", "eux", "fait", "faire", "faut", "fois", "font", "h", "https",
	"http", "ici", "il", "ils", "j", "je", "juste", "l", "la", "le", "les", "leur",
	"leurs", "lui", "ma", "mais", "me", "meme", "memes", "mes", "moi", "moins", "mon",
	"ne", "ni", "non", "nos", "notre", "nous", "on", "ont", "ou", "par", "parce",
	"pas", "peu", "peut", "plus", "plusieurs", "pour", "pourquoi", "pourra", "qu",
	"quand", "que", "quel", "quelle", "quelles", "quels", "qui", "quoi", "rt", "s",
	"sa", "sans", "se", "selon", "ses", "si", "sien", "son", "sont", "sous", "suis",
	"sur", "t", "ta", "te", "tellement", "tes", "toi", "ton", "toujours", "tous",
	"tout", "toute", "toutes", "tres", "trop", "tu", "un", "une", "va", "voici",
	"voila", "vont", "vos", "votre", "vous", "www", "y",
}

AGGRESSIVE_LEXICON = {
	"insulte": {
		"con", "connard", "connasse", "idiot", "idiote", "abruti", "abrutie",
		"cretin", "cretine", "debile", "imbecile", "minable", "pourriture",
		"ordure", "salaud", "salope", "raclure", "fdp", "pute", "encule",
		"enfoire", "clown", "ridicule", "pathetique", "nul", "nullite",
	},
	"violence_menace": {
		"tuer", "tuez", "mort", "crever", "pendre", "pendu", "bruler",
		"exploser", "detruire", "lyncher", "lynchage", "frapper", "violence",
		"menace", "menaces", "vengeance", "representailles", "guerre", "sang",
	},
	"accusation_grave": {
		"corrompu", "corrompue", "corruption", "mafia", "mafieux", "voleur",
		"voleurs", "escroc", "escroquerie", "criminel", "criminelle",
		"traitre", "complice", "complicite", "nazi", "facho", "fasciste",
		"dictature", "censure", "scandale", "honte", "honteux", "mensonge",
		"mensonges", "manipulation", "copinage", "collabo",
	},
	"appel_action": {
		"boycott", "boycotter", "dehors", "degage", "demission",
		"demissionner", "plainte", "justice", "proces",
	},
}
ALL_AGGRESSIVE_WORDS = set().union(*AGGRESSIVE_LEXICON.values())

_ACCENTS = str.maketrans("àâäéèêëïîôöùûüç", "aaaeeeeiioouuuc")


def _normalize_tokens(text: str) -> list[str]:
	text = text.lower().translate(_ACCENTS)
	return re.findall(r"[a-z]+", text)


def _save_fig(fig, name: str) -> None:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	path = OUTPUT_DIR / name
	fig.tight_layout()
	fig.savefig(path, dpi=120)
	print(f"[plot] {path}")
	# get_ipython() only exists inside a notebook/IPython session -> show inline there,
	# but stay silent (no GUI pop-up) when run as a plain script.
	try:
		get_ipython()
		plt.show()
	except NameError:
		pass
	plt.close(fig)


def _word_counts(texts, min_len: int = 3) -> Counter:
	counter = Counter()
	for text in texts:
		for tok in _normalize_tokens(text):
			if len(tok) >= min_len and tok not in FRENCH_STOPWORDS:
				counter[tok] += 1
	return counter


# ===================== Coordination =====================

def _synchronicity(df: pd.DataFrame, plot: bool, window: str = "5min", quantile: float = 0.95) -> pd.DataFrame:
	"""Rafales synchrones : beaucoup d'auteurs DIFFÉRENTS postent dans la même fenêtre courte."""
	print("--- Synchronicité (rafales multi-comptes) ---")
	ts = df.dropna(subset=["Date"])
	bins = ts["Date"].dt.floor(window)
	distinct_authors = ts.groupby(bins)["X Author ID"].nunique()
	threshold = distinct_authors.quantile(quantile)
	bursts = distinct_authors[distinct_authors >= threshold].sort_values(ascending=False)
	print(f"Fenêtres de {window} : {len(distinct_authors)} | seuil p{int(quantile * 100)} = {threshold:.0f} auteurs distincts")
	print(f"{len(bursts)} fenêtres synchrones au-dessus du seuil, ex. top 5 :")
	print(bursts.head(5))

	if plot:
		fig, ax = plt.subplots(figsize=(12, 4))
		distinct_authors.plot(ax=ax, color="steelblue", linewidth=0.8)
		ax.axhline(threshold, color="crimson", linestyle="--", label=f"seuil p{int(quantile * 100)} ({threshold:.0f})")
		ax.set_title(f"Synchronicité : auteurs distincts par fenêtre de {window}")
		ax.set_xlabel("Temps")
		ax.set_ylabel("Auteurs distincts")
		ax.legend()
		_save_fig(fig, "coordination_synchronicite.png")
	
	return bursts


def _rapid_fire(df: pd.DataFrame, plot: bool, threshold_s: int = 60) -> pd.DataFrame:
	"""Rafales rapid-fire : un même auteur enchaîne plusieurs posts en quelques secondes."""
	print("--- Rapid-fire (rafales mono-compte) ---")
	rf = df.dropna(subset=["Date"]).sort_values(["X Author ID", "Date"]).copy()
	rf["delta_s"] = rf.groupby("X Author ID")["Date"].diff().dt.total_seconds()

	rapid = rf[rf["delta_s"] <= threshold_s]
	per_author = rapid.groupby("X Author ID").size().sort_values(ascending=False)
	print(f"{len(rapid)} posts enchaînés en ≤ {threshold_s}s, par {rapid['X Author ID'].nunique()} comptes")
	print("Top comptes rapid-fire :")
	print(per_author.head(10))

	if plot:
		finite = rf["delta_s"].dropna()
		finite = finite[finite > 0]
		fig, ax = plt.subplots(figsize=(8, 4))
		bins = np.logspace(0, np.log10(finite.max()), 60) if len(finite) else [0, 1]
		ax.hist(finite, bins=bins, color="darkorange")
		ax.set_xscale("log")
		ax.axvline(threshold_s, color="crimson", linestyle="--", label=f"seuil rapid-fire ({threshold_s}s)")
		ax.set_title("Intervalle entre deux posts consécutifs d'un même auteur")
		ax.set_xlabel("Intervalle (s, échelle log)")
		ax.set_ylabel("Nombre de posts")
		ax.legend()
		_save_fig(fig, "coordination_rapid_fire.png")
	
	return per_author


def _copy_paste(df: pd.DataFrame, plot: bool, min_chars: int = 30, top_n: int = 15) -> dict:
	"""Messages identiques (hors retweets), à distinguer de deux façons :
	- inter-comptes : plusieurs comptes différents postent le même texte (coordination réelle) ;
	- intra-compte : un même compte ressasse le même texte (spam scripté / automation)."""
	print("--- Copier-coller (messages identiques, hors retweets) ---")
	cp = df[df["Engagement Type"] != "RETWEET"]
	cp = cp[cp["message_normalizer"].str.len() >= min_chars]

	cross_account = cp.groupby("message_normalizer")["X Author ID"].agg(["nunique", "count"])
	cross_account = cross_account[cross_account["nunique"] >= 2].sort_values("nunique", ascending=False)
	print(f"Inter-comptes : {len(cross_account)} messages identiques diffusés par ≥ 2 comptes différents ({cross_account['count'].sum()} posts concernés)")
	if len(cross_account):
		print(cross_account.head(10))

	same_account = cp.groupby(["X Author ID", "message_normalizer"]).size()
	same_account = same_account[same_account >= 2].sort_values(ascending=False)
	authors_spamming = same_account.index.get_level_values("X Author ID").nunique() if len(same_account) else 0
	print(f"Intra-compte : {len(same_account)} textes répétés ≥ 2 fois par le même compte, par {authors_spamming} comptes ({same_account.sum() if len(same_account) else 0} posts concernés)")

	if plot and (len(cross_account) or len(same_account)):
		fig, axes = plt.subplots(1, 2, figsize=(14, max(4, 0.3 * top_n)))

		top_cross = cross_account.head(top_n).iloc[::-1]
		if len(top_cross):
			axes[0].barh([f"cluster {i}" for i in range(len(top_cross), 0, -1)], top_cross["nunique"].values, color="seagreen")
		axes[0].set_title("Top clusters copiés-collés (comptes distincts)")
		axes[0].set_xlabel("Nombre de comptes distincts")

		top_same = same_account.head(top_n).iloc[::-1]
		if len(top_same):
			axes[1].barh([f"compte {i}" for i in range(len(top_same), 0, -1)], top_same.values, color="darkseagreen")
		axes[1].set_title("Top répétitions intra-compte (spam scripté)")
		axes[1].set_xlabel("Nombre de répétitions du même texte")

		_save_fig(fig, "coordination_copy_paste.png")
	
	return dict(cross_account=dict(texts=len(cross_account), posts=cross_account["count"].sum()),
				same_account=dict(texts=len(same_account), posts=same_account.sum() if len(same_account) else 0, authors=authors_spamming))


def _recent_accounts(df: pd.DataFrame, plot: bool, threshold_posts: int = 100) -> float:
	"""Comptes 'récents' : proxy via X Posts (volume de posts cumulé du compte au
	moment du tweet). Pas de date de création disponible dans le corpus."""
	print("--- Comptes récents (proxy X Posts) ---")
	acc = df.dropna(subset=["Date"]).copy()
	acc["recent"] = acc["X Posts"] <= threshold_posts
	share = acc["recent"].mean() * 100
	print(f"Seuil 'compte récent' de X Posts = {threshold_posts:.0f} posts cumulés")
	print(f"{share:.1f}% des tweets du corpus proviennent de comptes sous ce seuil")

	if plot:
		fig, axes = plt.subplots(1, 2, figsize=(14, 4))

		axes[0].hist(acc["X Posts"].clip(lower=1), bins=50, color="slateblue")
		axes[0].set_xscale("log")
		axes[0].axvline(threshold_posts, color="crimson", linestyle="--", label=f"seuil {threshold_posts} postes")
		axes[0].set_title("Distribution de X Posts (activité cumulée du compte)")
		axes[0].set_xlabel("X Posts (échelle log)")
		axes[0].set_ylabel("Nombre de tweets")
		axes[0].legend()

		daily = acc.groupby([acc["Date"].dt.date, "recent"]).size().unstack(fill_value=0)
		daily_share = daily.div(daily.sum(axis=1), axis=0) * 100
		if True in daily_share.columns:
			axes[1].plot(daily_share.index, daily_share[True], color="crimson")
		axes[1].set_title("Part quotidienne des tweets de comptes 'récents'")
		axes[1].set_xlabel("Date")
		axes[1].set_ylabel("% des tweets du jour")
		fig.autofmt_xdate()

		_save_fig(fig, "coordination_comptes_recents.png")
		
	return share


def coordination(data: pd.DataFrame, plot: bool = False):
	_synchronicity(data, plot)
	_rapid_fire(data, plot)
	_copy_paste(data, plot)
	_recent_accounts(data, plot)


# ===================== Sémantique =====================

def _dominant_vocabulary(df: pd.DataFrame, plot: bool, top_n: int = 25) -> list:
	print("--- Vocabulaire dominant ---")
	counts = _word_counts(df["Full Text"])
	top = counts.most_common(top_n)
	print(top[:15])

	if plot and top:
		words, freqs = zip(*top[::-1])
		fig, ax = plt.subplots(figsize=(8, max(4, 0.3 * len(words))))
		ax.barh(words, freqs, color="teal")
		ax.set_title(f"Top {top_n} mots les plus fréquents (hors stopwords)")
		ax.set_xlabel("Occurrences")
		_save_fig(fig, "semantic_vocabulaire_dominant.png")
	
	return top


def _vocabulary_shift(df: pd.DataFrame, plot: bool, top_n: int = 15, min_count: int = 15) -> dict:
	"""Glissement de vocabulaire entre la première et la seconde moitié chronologique du corpus."""
	print("--- Glissement de vocabulaire (1ère vs 2ème moitié de la période) ---")
	ts = df.dropna(subset=["Date"]).sort_values("Date")
	mid = len(ts) // 2
	first_half, second_half = ts.iloc[:mid], ts.iloc[mid:]

	counts_1 = _word_counts(first_half["Full Text"])
	counts_2 = _word_counts(second_half["Full Text"])
	total_1, total_2 = sum(counts_1.values()) or 1, sum(counts_2.values()) or 1

	words = {w for w, c in counts_1.items() if c >= min_count} | {w for w, c in counts_2.items() if c >= min_count}
	deltas = {
		w: (counts_2.get(w, 0) / total_2) - (counts_1.get(w, 0) / total_1)
		for w in words
	}
	rising = sorted(deltas.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
	fading = sorted(deltas.items(), key=lambda kv: kv[1])[:top_n]
	print(f"Mots en hausse (2ème moitié) : {rising[:10]}")
	print(f"Mots en baisse (2ème moitié) : {fading[:10]}")

	if plot and rising:
		words_r, deltas_r = zip(*rising[::-1])
		fig, ax = plt.subplots(figsize=(8, max(4, 0.3 * len(words_r))))
		ax.barh(words_r, [d * 100 for d in deltas_r], color="darkorange")
		ax.set_title("Mots dont la fréquence relative monte le plus (2ème moitié vs 1ère)")
		ax.set_xlabel("Variation de fréquence relative (points de %)")
		_save_fig(fig, "semantic_glissement_vocabulaire.png")
	
	return dict(rising=rising, fading=fading)


def _aggressiveness_scores(texts) -> tuple[list[float], Counter]:
	"""Score par tweet = nb de mots du lexique / nb de tokens, + compte par catégorie."""
	category_hits = Counter()
	scores = []
	for text in texts:
		toks = _normalize_tokens(text)
		hit_words = set(toks) & ALL_AGGRESSIVE_WORDS
		for cat, vocab in AGGRESSIVE_LEXICON.items():
			category_hits[cat] += len(hit_words & vocab)
		scores.append(len(hit_words) / len(toks) if toks else 0.0)
	return scores, category_hits


def _aggressiveness(df: pd.DataFrame, plot: bool) -> dict:
	print("--- Agressivité ---")
	scores, category_hits = _aggressiveness_scores(df["Full Text"])
	df = df.assign(_aggr_score=scores)
	share_aggressive = (df["_aggr_score"] > 0).mean() * 100
	print(f"{share_aggressive:.1f}% des tweets contiennent au moins un mot du lexique d'agressivité")
	print(f"Score moyen : {df['_aggr_score'].mean():.4f}")
	print(f"Répartition par catégorie (occurrences de mots) : {dict(category_hits)}")

	if plot:
		fig, axes = plt.subplots(1, 2, figsize=(14, 4))

		cats = list(category_hits.keys())
		axes[0].bar(cats, [category_hits[c] for c in cats], color="indianred")
		axes[0].set_title("Occurrences de mots agressifs par catégorie")
		axes[0].set_ylabel("Occurrences")
		axes[0].tick_params(axis="x", rotation=30)

		daily = df.dropna(subset=["Date"]).groupby(df["Date"].dt.date)["_aggr_score"].mean()
		axes[1].plot(daily.index, daily.values, color="indianred")
		axes[1].set_title("Score d'agressivité moyen par jour")
		axes[1].set_xlabel("Date")
		axes[1].set_ylabel("Score moyen")
		fig.autofmt_xdate()

		_save_fig(fig, "semantic_agressivite.png")
	
	return dict(category_hits)


def _escalation(df: pd.DataFrame, plot: bool) -> float:
	"""Montée en tension : part de sentiment négatif + agressivité lexicale, jour par jour."""
	print("--- Escalade du ton ---")
	ts = df.dropna(subset=["Date"]).copy()
	ts["_aggr_score"], _ = _aggressiveness_scores(ts["Full Text"])

	daily_negative = ts.groupby(ts["Date"].dt.date)["Sentiment"].apply(lambda s: (s == "negative").mean() * 100)
	daily_aggr = ts.groupby(ts["Date"].dt.date)["_aggr_score"].mean()

	first_half_neg, second_half_neg = daily_negative.iloc[: len(daily_negative) // 2].mean(), daily_negative.iloc[len(daily_negative) // 2 :].mean()
	neg_evolution = (second_half_neg - first_half_neg) / first_half_neg
	print(f"Part de sentiment négatif : {first_half_neg:.1f}% (1ère moitié de la période) -> {second_half_neg:.1f}% (2ème moitié)")
	print(f"Evolution de la part de sentiment négatif : {'+' if neg_evolution > 0 else ''}{neg_evolution*100:.2f} %")

	if plot:
		fig, ax1 = plt.subplots(figsize=(12, 4))
		ax1.plot(daily_negative.index, daily_negative.values, color="crimson", label="% sentiment négatif")
		ax1.set_ylabel("% sentiment négatif", color="crimson")
		ax1.set_xlabel("Date")

		ax2 = ax1.twinx()
		ax2.plot(daily_aggr.index, daily_aggr.values, color="navy", linestyle="--", label="score d'agressivité moyen")
		ax2.set_ylabel("Score d'agressivité moyen", color="navy")

		fig.legend(loc="upper left")
		ax1.set_title("Escalade du ton : sentiment négatif et agressivité lexicale, jour par jour")
		fig.autofmt_xdate()
		_save_fig(fig, "semantic_escalade.png")
	
	return neg_evolution


def semantic(data: pd.DataFrame, plot: bool = False):
	_dominant_vocabulary(data, plot)
	_vocabulary_shift(data, plot)
	_aggressiveness(data, plot)
	_escalation(data, plot)


def main():
	data = load_corpus()
	data = data.drop(["Impressions", "Gender"], axis=1)  # Données non exploitables
	data = data.drop(["City", "City Code"], axis=1)  # Trop de valeurs manquantes pour les villes
	data = data.drop(["Domain", "Language", "Country"], axis=1)  # Valeur constante dans le dataset pour ce cas
	print("=================== Coordination ================")
	coordination(data, plot=True)
	print("\n=================== Semantic ====================")
	semantic(data, plot=True)


if __name__ == '__main__':
	main()
