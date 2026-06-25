# Guide d'utilisation — Pipeline de gestion de crise

Ce guide explique comment installer, configurer et lancer le pipeline de A à Z,
et comment l'adapter à une nouvelle crise en quelques minutes.

> **État du projet (J2)**
> - ✅ Backend complet : 4 agents LLM branchés, pipeline bout en bout fonctionnel
> - 🔧 Frontend : scaffold React 19 + Vite posé, interface à construire

---

## Structure du repo

```
Datathon/
├── backend/                  # Pipeline Python (tout ce qui tourne côté serveur)
│   ├── src/
│   │   ├── main.py           # Point d'entrée — pipeline CLI complet
│   │   ├── agents/
│   │   │   ├── analyste.py   # Classifie les tweets par narratif
│   │   │   ├── veille.py     # Détecte pics de volume et viraux
│   │   │   ├── stratege.py   # Propose 3 options de réponse
│   │   │   └── redacteur.py  # Rédige les communiqués
│   │   ├── pipeline/
│   │   │   ├── state.py      # CrisisState — typage partagé entre agents
│   │   │   ├── schemas.py    # Contrats Pydantic de tous les agents
│   │   │   └── graph.py      # LangGraph StateGraph
│   │   ├── prompts/
│   │   │   └── prompts.py    # System prompts + factory LLM (GROQ/GEMINI)
│   │   └── tools/
│   │       └── corpus_loader.py  # Chargement et nettoyage du dataset
│   ├── notebooks/
│   │   ├── J1_exploration.ipynb      # Exploration initiale du corpus
│   │   ├── J2_narratifs.ipynb        # Validation des narratifs, figures
│   │   └── tuning_veille.ipynb       # Calibration des seuils de l'agent Veille
│   ├── Dataset/              # gitignored — placer data.xlsx ici
│   ├── outputs/              # gitignored — JSON générés à chaque run
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Interface React 19 + Vite + TypeScript (en cours)
│   └── src/
├── docs/                     # Rapports, planning, ce guide
└── slides/                   # Présentation HTML + figures
    ├── presentation.html     # Navigable au clavier (← →)
    └── figures/
```

---

## 1. Prérequis

| Outil   | Version minimale |
|---------|-----------------|
| Python  | 3.11+           |
| Git     | —               |
| Node.js | 18+ (frontend uniquement) |
| pnpm    | 9+ (frontend uniquement)  |

Une clé API **GROQ** (gratuit) **ou** **GEMINI** (Google AI Studio) suffit pour le backend.

---

## 2. Installation backend

```bash
git clone https://github.com/ValetteL/Datathon.git
cd Datathon/backend
pip install -r requirements.txt
```

### Configurer l'environnement

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

### Placer le dataset

Déposer `data.xlsx` dans `backend/Dataset/`.

Vérification :

```python
# Depuis backend/
from src.tools.corpus_loader import load_corpus
df = load_corpus("Dataset/data.xlsx")
# → doit afficher : 35 396 tweets | 2026-03-19 → 2026-05-01
```

---

## 3. Lancer le pipeline

```bash
# Depuis backend/
python src/main.py
```

Le pipeline s'exécute en 4 étapes avec validation humaine intermédiaire :

```
📥 Corpus chargé (35 396 tweets)
  ↓
🔍 Agent Analyste  — classe chaque tweet par narratif (censure / copinage / …)
  ↓
📡 Agent Veille    — détecte les pics de volume et tweets viraux
  ↓
🧑‍⚖️ Human Gate   — l'opérateur valide ou rejette l'analyse (obligatoire)
  ↓
🧭 Agent Stratège  — propose 3 options de réponse (prudent / équilibré / assertif)
  ↓
✍️ Agent Rédacteur — rédige 3 versions de communiqué calées sur les options
```

### Ce que vous verrez dans le terminal

- Un spinner et un timing pour chaque appel LLM
- Un tableau de répartition des narratifs (Analyste)
- Un panel d'alerte avec niveau `low / medium / high / critical` (Veille)
- Les 3 options stratégiques avec leurs risques (Stratège)
- Les 3 communiqués prêts à l'emploi (Rédacteur)
- Un récapitulatif final (run ID, narratif dominant, niveau d'alerte, temps total)

### Outputs sauvegardés automatiquement

À la fin de chaque run, 4 fichiers JSON sont écrits dans `backend/outputs/` :

```
backend/outputs/
  narratives_<run_id>.json    ← classifications de l'Analyste
  alerts_<run_id>.json        ← alertes de la Veille
  strategy_<run_id>.json      ← options du Stratège
  drafts_<run_id>.json        ← communiqués du Rédacteur
```

Le `run_id` (8 caractères) est affiché en début d'exécution.
Ces fichiers permettent de relire ou déboguer n'importe quelle exécution passée
**sans relancer les LLM**.

---

## 4. Adapter à une nouvelle crise

Le seul paramètre à changer dans `backend/src/main.py` (ligne ~25) :

```python
state = CrisisState(
    corpus_config={
        "evenement": "Affaire Ultia x CNC",   # ← nom de la crise
        "periode": "mars-avril 2026",          # ← période couverte
    },
    ...
)
```

Ce paramètre reconfigure les prompts de **tous les agents** automatiquement.

### Changer le corpus

Remplacer `backend/Dataset/data.xlsx` par le nouveau fichier.
Le `corpus_loader` attend ces colonnes :

| Colonne | Rôle |
|---|---|
| `Date` | Horodatage du tweet |
| `Full Text` / `message_normalizer` | Contenu textuel |
| `Engagement Type` | RETWEET / REPLY / QUOTE / ORIGINAL |
| `Likes`, `Shares` | Métriques d'engagement |
| `Sentiment` | neutral / negative / positive |
| `postID` | Identifiant unique du tweet |
| `Author`, `X Followers`, `X Verified` | Profil de l'auteur |

### Recalibrer les seuils de l'Agent Veille

Les seuils actuels sont calibrés sur la crise Ultia × CNC.
Pour un nouveau corpus, lancer le notebook de calibration :

```bash
# Depuis backend/
jupyter notebook notebooks/tuning_veille.ipynb
```

Il calcule des seuils statistiques adaptés (`mean + 2σ`, percentiles sur non-nuls)
et exporte `outputs/thresholds_veille.json`.

Découverte clé sur le corpus actuel : **5 jours ont un RT ratio > 90% sans pic de volume**
— ces précurseurs d'amplification sont actuellement ignorés par `is_alert`. Le notebook
les identifie et propose de les inclure dans la logique d'alerte.

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
os.chdir('/content/Datathon/backend')

from google.colab import userdata
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
os.environ['IA_PROVIDER'] = 'GEMINI'

# Lancer le pipeline
exec(open('src/main.py').read())
```

Colab Secrets → ajouter `GOOGLE_API_KEY` (ou `GROQ_API_KEY`).
Télécharger `data.xlsx` depuis le Drive partagé et le déposer dans `backend/Dataset/`.

---

## 7. Frontend (en cours)

Le frontend React 19 + Vite + TypeScript est initialisé dans `frontend/`.

```bash
# Depuis la racine du repo
cd frontend
pnpm install
pnpm dev      # → http://localhost:5173
```

L'interface est à construire — le scaffold est posé, les composants métier restent à implémenter.

---

## 8. Présentation

```bash
# Ouvrir directement dans le navigateur
slides/presentation.html
```

Navigation : flèches ← → ou clic sur les boutons. La présentation est auto-contenue (HTML pur).
