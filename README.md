# Affaire Ultia × CNC — Analyse de crise multi-agents

Pipeline LangGraph d'analyse de crise réseaux sociaux (~35k tweets, mars-avril 2026).  
Classifie les narratifs, détecte les signaux d'alerte, et génère des projets de réponse institutionnelle avec une validation humaine obligatoire.

**Équipe** : Alexis (P1), Franck (P2), Ruben (P3), Malo (P4), Baptiste (P5), Louis (chef de projet).

---

## Structure du repo

```
Datathon/
├── backend/          # Pipeline LangGraph + API FastAPI (Python)
│   ├── src/
│   │   ├── agents/   # veille, analyste, stratege, redacteur
│   │   ├── pipeline/ # LangGraph StateGraph + CrisisState
│   │   ├── prompts/  # get_llm() + get_system_prompt()
│   │   ├── tools/    # corpus_loader.py
│   │   └── main.py   # Démo interactive (rich terminal)
│   ├── notebooks/    # EDA J1 + analyse J2
│   ├── Dataset/      # gitignored — partager via Teams/Drive
│   ├── outputs/      # gitignored — générés à l'exécution
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Interface React 19 + Vite + TypeScript
│   ├── src/
│   └── package.json
├── docs/             # Rapports, planning, PDFs
└── slides/           # Figures + données clés pour la présentation
```

---

## Prérequis

| Outil   | Version minimale     |
| ------- | -------------------- |
| Python  | 3.11+                |
| Node.js | 18+                  |
| pnpm    | 9+ (`npm i -g pnpm`) |

---

## Backend

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Éditer .env : renseigner IA_PROVIDER + la clé API correspondante
```

Variables requises dans `.env` :

| Variable         | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| `IA_PROVIDER`    | `GROQ` (défaut) ou `GEMINI`                                     |
| `GROQ_API_KEY`   | Clé Groq — [console.groq.com](https://console.groq.com)         |
| `GOOGLE_API_KEY` | Clé Gemini — [aistudio.google.com](https://aistudio.google.com) |
| `GROQ_MODEL`     | Optionnel — défaut : `llama-3.3-70b-versatile`                  |
| `GEMINI_MODEL`   | Optionnel — défaut : `gemini-2.0-flash`                         |

### Validation de l'installation

```bash
# Depuis backend/ — lance le pipeline complet en mode CLI
python src/main.py
```

Pour un check rapide sans dataset :

```bash
cd backend
python - <<'EOF'
import sys; sys.path.insert(0, "src")
from prompts.prompts import get_llm
llm = get_llm()
print(llm.invoke("Réponds juste OK.").content)
EOF
```

### Lancement

**Démo interactive (terminal rich — pipeline complet avec gate humaine) :**

```bash
cd backend
python src/main.py
```

**API FastAPI** _(à venir — `src/api/main.py` pas encore créé)_ :

```bash
cd backend
uvicorn src.api.main:app --reload --port 8000
```

---

## Frontend

### Installation

```bash
cd frontend
pnpm install
```

### Lancement

```bash
pnpm dev
# → http://localhost:5173
```

### Build de production

```bash
pnpm build
pnpm preview
```

---

## Lancement complet (dev)

Ouvrir deux terminaux depuis la racine :

```bash
# Terminal 1 — Backend
cd backend && source .venv/bin/activate && python src/main.py

# Terminal 2 — Frontend
cd frontend && pnpm dev
```

Quand l'API FastAPI sera exposée, le frontend appellera `http://localhost:8000`.  
Un proxy Vite peut être configuré dans `frontend/vite.config.ts` pour éviter les problèmes CORS en dev.

---

## Pipeline LangGraph

```
Dataset/data.xlsx
  → load_corpus()        # seul point d'entrée pour les données brutes
  → AgentAnalyste        # classifie les narratifs (censure / copinage / …)
  → AgentVeille          # détecte les signaux d'alerte
  → HumanGate (pause)    # validation humaine obligatoire (yes/no)
  → AgentStratège        # génère les options de réponse
  → AgentRédacteur       # rédige les communiqués
  → save_outputs()       # outputs/<key>_<run_id>.json
```
