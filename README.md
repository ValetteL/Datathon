# Affaire Ultia × CNC — Analyse de crise multi-agents

Pipeline LangGraph + interface React d'analyse de crise réseaux sociaux (~35 000 tweets, mars-avril 2026). Classifie les narratifs, détecte les signaux d'alerte, génère des projets de réponse institutionnelle avec une validation humaine obligatoire.

**Équipe** : Alexis (P1 — temporalité), Franck (P2 — narratifs/sémantique), Ruben (P3 — acteurs/analyste), Malo (P4 — coordination/veille), Baptiste (P5 — orchestration/stratège/rédacteur), Louis (chef de projet / intégration).

---

## Démarrage rapide

> Prérequis : Python 3.11+, Node.js 18+, pnpm 9+ (`npm i -g pnpm`)

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner GROQ_API_KEY ou GOOGLE_API_KEY
uvicorn main:app --reload --port 8000
```

**Frontend** (dans un second terminal)

```bash
cd frontend
pnpm install
pnpm dev
```

L'interface est disponible sur **http://localhost:5173**, l'API sur **http://localhost:8000** (Swagger : `/docs`).

---

## Pipeline

```
Dataset/data.xlsx
  → AgentAnalyste   # classifie les narratifs (censure / copinage / …)
  → AgentVeille     # détecte pics et signaux d'alerte
  → HumanGate       # validation humaine obligatoire : valider ou rejeter
  → AgentStratège   # génère 3 options de réponse institutionnelle
  → AgentRédacteur  # rédige les communiqués
  → outputs/        # sessions JSON persistées sur disque
```

---

## Structure du repo

```
Datathon/
├── backend/             # API FastAPI + pipeline LangGraph
│   ├── main.py          # point d'entrée — uvicorn main:app
│   ├── src/
│   │   ├── agents/      # analyste · veille · stratege · redacteur
│   │   ├── pipeline/    # CrisisState · session_store (persistance disque)
│   │   ├── schemas/     # Pydantic requêtes/réponses
│   │   ├── tools/       # corpus_loader.py
│   │   └── prompts/     # get_llm() · get_system_prompt()
│   ├── outputs/         # gitignored — sessions persistées ici
│   ├── Dataset/         # gitignored — partager via Teams/Drive
│   └── notebooks/       # EDA J1 + analyse J2
├── frontend/            # React 19 + TypeScript + Vite + TailwindCSS
│   └── src/
│       ├── api/         # client.ts · types.ts
│       ├── components/  # CollapsibleCard · HumanGate · StepIndicator…
│       ├── hooks/       # usePipeline.ts
│       └── pages/       # Pipeline.tsx
├── docs/                # Rapport J1 · planning sprint
└── slides/              # Figures · chiffres_cles.json
```

---

## Configuration `.env`

| Variable         | Valeur                                   |
| ---------------- | ---------------------------------------- |
| `IA_PROVIDER`    | `GROQ` (défaut) ou `GEMINI`              |
| `GROQ_API_KEY`   | Clé Groq — console.groq.com              |
| `GOOGLE_API_KEY` | Clé Gemini — aistudio.google.com         |
| `GROQ_MODEL`     | Optionnel — défaut `llama-3.3-70b-versatile` |
| `GEMINI_MODEL`   | Optionnel — défaut `gemini-2.0-flash`    |

---

## Documentation

| Fichier | Contenu |
| ------- | ------- |
| `backend/README.md` | API, endpoints, schémas, session store |
| `frontend/README.md` | Composants, machine d'états, appels API |
| `docs/RAPPORT_J1.md` | Analyse J1 : corpus, chiffres clés, grille 5 axes |
| `docs/planning.md` | Planning sprint par personne |
| `backend/SPRINT.md` | Brief d'équipe — setup et tâches J3 restantes |
