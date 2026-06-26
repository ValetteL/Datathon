# Guide d'utilisation — Pipeline de gestion de crise

> **État du projet (J2)**  
> ✅ Backend complet — 4 agents LLM branchés, pipeline bout en bout fonctionnel  
> 🔧 Frontend — scaffold React 19 + Vite posé, interface à construire

---

## Structure réelle du repo

```
Datathon/                         ← racine — lancer les scripts depuis ici
├── backend/
│   ├── src/
│   │   ├── main.py               # Point d'entrée du pipeline
│   │   ├── agents/
│   │   │   ├── analyste.py
│   │   │   ├── veille.py
│   │   │   ├── stratege.py
│   │   │   └── redacteur.py
│   │   ├── pipeline/
│   │   │   ├── state.py          # CrisisState TypedDict
│   │   │   ├── schemas.py        # Contrats Pydantic de tous les agents
│   │   │   └── graph.py          # LangGraph StateGraph
│   │   ├── prompts/
│   │   │   └── prompts.py        # System prompts + factory LLM
│   │   └── tools/
│   │       ├── corpus_loader.py
│   │       └── thresholds.py         # Seuils dynamiques auto-calibrés (avec cache)
│   ├── notebooks/
│   │   ├── J1_exploration.ipynb
│   │   ├── J2_narratifs.ipynb
│   │   ├── J3_acteurs.ipynb          # Analyse acteurs (proxy stat, 5 types, sans LLM)
│   │   ├── Exploration_coord_sem.ipynb
│   │   └── tuning_veille.ipynb       # Exploration calibration seuils (référence)
│   └── requirements.txt
├── frontend/                     # React 19 + Vite (scaffold, en cours)
├── Dataset/                      # gitignored — data.xlsx à placer ici
├── outputs/                      # gitignored — JSON générés à chaque run
├── slides/
│   ├── presentation.html         # Présentation navigable (← →)
│   └── figures/
└── docs/
    └── GUIDE_UTILISATION.md      # Ce fichier
```

---

## 1. Prérequis

- Python 3.11+
- Une clé API **GROQ** (gratuit) **ou** **GEMINI** (Google AI Studio)
- Node.js 18+ + pnpm 9+ (frontend uniquement)

---

## 2. Installation

```bash
git clone https://github.com/ValetteL/Datathon.git
cd Datathon
pip install -r backend/requirements.txt
```

### Configurer l'environnement

```bash
cp backend/.env.example backend/.env
```

Ouvrir `backend/.env` et renseigner :

```env
# Choisir le provider : GEMINI ou GROQ
IA_PROVIDER=GEMINI

# Si GEMINI → https://aistudio.google.com → "Get API key"
GOOGLE_API_KEY=ta_cle_ici

# Si GROQ → https://console.groq.com → API Keys
GROQ_API_KEY=ta_cle_ici
```

### Placer le dataset

Copier `data.xlsx` dans `Dataset/` (à la racine du repo, pas dans `backend/`).

Vérification :

```bash
# Depuis la racine du repo
python -c "
import sys; sys.path.insert(0, 'backend/src')
from tools.corpus_loader import load_corpus
df = load_corpus('Dataset/data.xlsx')
"
# → doit afficher : 35 396 tweets | 2026-03-19 → 2026-05-01
```

---

## 3. Lancer le pipeline

```bash
# Depuis la racine du repo (important — Dataset/ est à la racine)
python backend/src/main.py
```

Le pipeline s'exécute en 4 étapes :

```
📥 Corpus chargé (35 396 tweets)
  ↓
🔍 Agent Analyste  — classifie les tweets par narratif (censure / copinage / …)
  ↓
📡 Agent Veille    — détecte les pics de volume, tweets viraux et signaux de coordination
  ↓
🧑‍⚖️ Human Gate   — l'opérateur valide ou rejette l'analyse (obligatoire)
  ↓
🧭 Agent Stratège  — propose 3 options de réponse (prudent / équilibré / assertif)
  ↓
✍️ Agent Rédacteur — rédige 3 versions de communiqué
```

### Outputs sauvegardés automatiquement

À la fin de chaque run, 4 fichiers JSON dans `outputs/` :

```
outputs/
  narratives_<run_id>.json
  alerts_<run_id>.json
  strategy_<run_id>.json
  drafts_<run_id>.json
```

Le `run_id` (8 caractères) s'affiche en début d'exécution.
Ces fichiers permettent d'inspecter ou déboguer une exécution passée sans relancer les LLM.

---

## 4. Adapter à une nouvelle crise

Un seul paramètre à changer dans `backend/src/main.py` (ligne ~25) :

```python
corpus_config={
    "evenement": "Affaire Ultia x CNC",   # ← nom de la crise
    "periode": "mars-avril 2026",          # ← période couverte
},
```

Ce paramètre reconfigure les prompts de **tous les agents** automatiquement.

### Changer le corpus

Remplacer `Dataset/data.xlsx`. Le `corpus_loader` attend ces colonnes :

| Colonne | Rôle |
|---|---|
| `Date` | Horodatage du tweet |
| `Full Text` / `message_normalizer` | Contenu textuel |
| `Engagement Type` | RETWEET / REPLY / QUOTE / ORIGINAL |
| `Likes`, `Shares` | Métriques d'engagement |
| `Sentiment` | neutral / negative / positive |
| `postID` | Identifiant unique du tweet |
| `Author`, `X Followers`, `X Verified`, `X Posts`, `X Author ID` | Profil de l'auteur (X Posts utilisé pour proxy acteur suspect) |

### Recalibrer les seuils de l'Agent Veille

**Aucune action requise** — les seuils se calibrent automatiquement au premier lancement.

`tools/thresholds.py` calcule les seuils statistiques au démarrage du pipeline et met le résultat en cache dans `outputs/thresholds_<hash>.json`. Si le corpus change, le cache est invalidé et le calcul relance seul.

Seuils calculés automatiquement :
- **Volume** : `mean + 2σ` sur la distribution journalière (granularité `daily` / `weekly` / `monthly` selon la durée du corpus)
- **Viraux** : percentile p90 sur Likes non-nuls, p75 sur Shares non-nuls
- **Coordination** : synchronicité p95, seuil rapid-fire 1% des auteurs, copy-paste inter-comptes
- **Acteurs** : seuil d'influencer burst (p90 influenceurs distincts/30min), cascade sentiment vérifiés (mean+1.5σ)

Pour inspecter ou forcer un recalcul :

```python
from src.tools.thresholds import compute_thresholds
from src.tools.corpus_loader import load_corpus

df = load_corpus("Dataset/data.xlsx")
t = compute_thresholds(df, force=True)   # force=True ignore le cache
print(t)
```

Le notebook `tuning_veille.ipynb` reste utile pour **explorer** la calibration et visualiser les distributions — mais il n'est plus nécessaire pour le fonctionnement du pipeline.

---

## 5. Changer le provider LLM

Dans `backend/.env` :

```env
IA_PROVIDER=GROQ    # llama-3.3-70b-versatile par défaut
# ou
IA_PROVIDER=GEMINI  # gemini-2.0-flash par défaut
```

Pour forcer un modèle spécifique :

```env
GROQ_MODEL=llama3-70b-8192
GEMINI_MODEL=gemini-2.5-flash
```

---

## 6. Sur Google Colab

```python
import sys, os
sys.path.insert(0, '/content/Datathon/backend/src')
os.chdir('/content/Datathon')  # important — Dataset/ est à la racine

from google.colab import userdata
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
os.environ['IA_PROVIDER'] = 'GEMINI'

exec(open('backend/src/main.py').read())
```

Colab Secrets → ajouter `GOOGLE_API_KEY` (ou `GROQ_API_KEY`).  
Télécharger `data.xlsx` depuis le Drive partagé et le déposer dans `Dataset/` (à la racine).

---

## 7. Frontend (en cours)

```bash
cd frontend
pnpm install
pnpm dev      # → http://localhost:5173
```

L'interface est à construire — le scaffold React 19 + Vite est posé.

---

## 8. Présentation

```bash
# Ouvrir directement dans le navigateur
slides/presentation.html
```

Navigation : flèches ← → ou clic sur les boutons. HTML pur, aucune dépendance.
