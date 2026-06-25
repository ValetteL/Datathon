# Guide d'utilisation — Pipeline de gestion de crise

Ce guide explique comment installer, configurer et lancer le pipeline de A à Z,
et comment l'adapter à une nouvelle crise en quelques minutes.

---

## 1. Prérequis

- Python 3.11+
- Git
- Une clé API **GROQ** (gratuit) **ou** **GEMINI** (Google AI Studio)

---

## 2. Installation

```bash
git clone https://github.com/ValetteL/Datathon.git
cd Datathon
pip install -r requirements.txt
```

---

## 3. Configuration

### 3.1 Créer le fichier `.env`

```bash
cp .env.example .env
```

Ouvrir `.env` et renseigner :

```env
# Choisir le provider : GEMINI ou GROQ
IA_PROVIDER=GEMINI

# Si GEMINI — obtenir sur https://aistudio.google.com → "Get API key"
GOOGLE_API_KEY=ta_cle_ici

# Si GROQ — obtenir sur https://console.groq.com → API Keys
GROQ_API_KEY=ta_cle_ici
```

Un seul provider suffit. Le pipeline bascule automatiquement selon `IA_PROVIDER`.

### 3.2 Placer le dataset

Le fichier `Dataset/data.xlsx` doit être présent à la racine du repo.
Sur Colab, le télécharger depuis le Drive partagé et le déposer dans `Dataset/`.

Vérification rapide :

```python
from src.tools.corpus_loader import load_corpus
df = load_corpus("Dataset/data.xlsx")
# → doit afficher : 35 396 tweets | 2026-03-19 → 2026-05-01
```

---

## 4. Lancer le pipeline

```bash
cd src
python main.py
```

Le pipeline s'exécute en 4 étapes :

```
📥 Corpus chargé (35 396 tweets)
  ↓
🔍 Agent Analyste  — classe chaque tweet par narratif (censure / copinage / …)
  ↓
📡 Agent Veille    — détecte les pics de volume et tweets viraux
  ↓
🧑‍⚖️ Human Gate   — YOU validez ou rejetez l'analyse avant de continuer
  ↓
🧭 Agent Stratège  — propose 3 options de réponse (prudent / équilibré / assertif)
  ↓
✍️ Agent Rédacteur — rédige 3 versions de communiqué calées sur les options
```

### Ce que vous verrez dans le terminal

- Un spinner pendant chaque appel LLM
- Un tableau de répartition des narratifs
- Un panel d'alerte avec niveau (low / medium / high / critical)
- Les 3 options stratégiques avec leurs risques
- Les 3 communiqués prêts à l'emploi
- Un récapitulatif final avec les temps par agent

### Outputs sauvegardés automatiquement

À la fin de chaque run, 4 fichiers JSON sont écrits dans `outputs/` :

```
outputs/
  narratives_<run_id>.json    ← classifications de l'Analyste
  alerts_<run_id>.json        ← alertes de la Veille
  strategy_<run_id>.json      ← options du Stratège
  drafts_<run_id>.json        ← communiqués du Rédacteur
```

Le `run_id` est affiché en début d'exécution. Ces fichiers permettent de relire
ou déboguer n'importe quelle exécution passée sans relancer les LLM.

---

## 5. Adapter à une nouvelle crise

C'est le paramètre central dans `src/main.py`, ligne 25 :

```python
state = CrisisState(
    raw_df=df,
    tweets_sample=df.sample(200, random_state=42),
    corpus_config={
        "evenement": "Affaire Ultia x CNC",   # ← changer le nom de la crise
        "periode": "mars-avril 2026",          # ← changer la période
    },
    ...
)
```

Changer `evenement` et `periode` reconfigure les prompts de tous les agents.
Le corpus (`data.xlsx`) et les seuils de veille sont les seuls autres paramètres à adapter.

### Changer le corpus

Remplacer `Dataset/data.xlsx` par le nouveau fichier. Le `corpus_loader` attend ces colonnes :

| Colonne | Rôle |
|---|---|
| `Date` | Horodatage du tweet (datetime) |
| `Full Text` / `message_normalizer` | Contenu textuel |
| `Engagement Type` | RETWEET / REPLY / QUOTE / ORIGINAL |
| `Likes`, `Shares` | Métriques d'engagement |
| `Sentiment` | neutral / negative / positive |
| `postID` | Identifiant unique du tweet |
| `Author`, `X Followers`, `X Verified` | Profil de l'auteur |

### Recalibrer les seuils de l'Agent Veille

Les seuils actuels (`VOLUME_ALERT_PER_DAY`, `VIRAL_LIKES_THRESHOLD`, etc.) sont calibrés
sur le corpus Ultia × CNC. Pour un nouveau corpus, lancer le notebook de calibration :

```bash
jupyter notebook notebooks/tuning_veille.ipynb
```

Il calcule des seuils statistiques adaptés au corpus (`mean + 2σ`, percentiles sur non-nuls)
et exporte un fichier `outputs/thresholds_veille.json` prêt à l'emploi.

---

## 6. Changer le provider LLM

Dans `.env`, modifier simplement `IA_PROVIDER` :

```env
IA_PROVIDER=GROQ    # llama-3.3-70b-versatile par défaut
# ou
IA_PROVIDER=GEMINI  # gemini-2.0-flash par défaut
```

Pour forcer un modèle spécifique :

```env
GROQ_MODEL=llama3-70b-8192
# ou
GEMINI_MODEL=gemini-2.5-flash
```

---

## 7. Sur Google Colab

```python
# En tête de notebook
import sys, os
sys.path.insert(0, '/content/Datathon/src')
os.chdir('/content/Datathon')

from google.colab import userdata
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
os.environ['IA_PROVIDER'] = 'GEMINI'
```

Le pipeline `main.py` peut s'exécuter tel quel dans une cellule Colab.
Penser à charger `Dataset/data.xlsx` depuis le Drive partagé avant de lancer.

---

## 8. Structure du projet

```
Datathon/
├── Dataset/
│   └── data.xlsx               # Corpus de tweets (ne pas committer)
├── src/
│   ├── main.py                 # Point d'entrée — lance le pipeline complet
│   ├── agents/
│   │   ├── analyste.py         # Classifie les tweets par narratif
│   │   ├── veille.py           # Détecte pics et viraux
│   │   ├── stratege.py         # Propose 3 options de réponse
│   │   └── redacteur.py        # Rédige les communiqués
│   ├── pipeline/
│   │   ├── state.py            # CrisisState — le typage partagé entre agents
│   │   └── schemas.py          # Contrats Pydantic (NarrativeResult, etc.)
│   ├── prompts/
│   │   └── prompts.py          # System prompts + factory LLM (GROQ/GEMINI)
│   └── tools/
│       └── corpus_loader.py    # Chargement et nettoyage du dataset
├── notebooks/
│   ├── J1_exploration.ipynb    # Exploration initiale du corpus
│   ├── J2_narratifs.ipynb      # Validation des narratifs, figures
│   └── tuning_veille.ipynb     # Calibration des seuils de l'agent Veille
├── outputs/                    # JSON générés par chaque run (gitignorés)
├── slides/
│   ├── presentation.html       # Présentation navigable (flèches / clavier)
│   └── figures/                # Figures exportées par les notebooks
├── docs/
│   ├── GUIDE_UTILISATION.md    # Ce fichier
│   └── RAPPORT_J1.md           # Rapport d'analyse J1
├── .env.example                # Template de configuration (copier en .env)
└── requirements.txt
```
