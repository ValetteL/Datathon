# Backend — Datathon CNC × Ultia

API FastAPI exposant le pipeline multi-agents d'analyse de crise virale.

## Stack

Python 3.11+ · FastAPI · Uvicorn · LangChain · LangGraph · Pydantic v2 · pandas

## Démarrage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # renseigner IA_PROVIDER + clé API
uvicorn main:app --reload --port 8000
```

Le corpus (`Dataset/data.xlsx`) est chargé une seule fois au démarrage.  
Swagger : http://localhost:8000/docs

## Variables d'environnement

| Variable | Description |
| --- | --- |
| `IA_PROVIDER` | `GROQ` (défaut) ou `GEMINI` |
| `GROQ_API_KEY` | Clé Groq — console.groq.com |
| `GOOGLE_API_KEY` | Clé Gemini — aistudio.google.com |
| `GROQ_MODEL` | Optionnel — défaut `llama-3.3-70b-versatile` |
| `GEMINI_MODEL` | Optionnel — défaut `gemini-2.0-flash` |

---

## Architecture

```
backend/
├── main.py                   # FastAPI app · lifespan · routes
└── src/
    ├── agents/
    │   ├── analyste.py       # run_analyste() → NarrativeResult
    │   ├── veille.py         # run_veille()   → AlertSignal
    │   ├── stratege.py       # run_stratege() → StrategyOptions
    │   └── redacteur.py      # run_redacteur() → DraftCommunique
    ├── pipeline/
    │   ├── state.py          # CrisisState TypedDict
    │   └── session_store.py  # persistance JSON dans outputs/
    ├── schemas/
    │   ├── requests.py       # corps de requêtes Pydantic
    │   └── responses.py      # réponses Pydantic
    ├── tools/
    │   └── corpus_loader.py  # load_corpus() — seul point d'entrée
    └── prompts/
        └── prompts.py        # get_llm() · get_system_prompt()
```

---

## Endpoints

| Méthode | Route | Description |
| --- | --- | --- |
| `POST` | `/analyse/analyste` | Lance AgentAnalyste, crée un `run_id` |
| `POST` | `/analyse/veille` | Lance AgentVeille sur un `run_id` existant |
| `POST` | `/analyse/rejeter` | Marque la session comme rejetée |
| `POST` | `/analyse/stratege` | Lance AgentStratège (requiert `humain_approved: true`) |
| `POST` | `/analyse/redacteur` | Lance AgentRédacteur |
| `GET` | `/sessions` | Liste toutes les sessions persistées |
| `GET` | `/sessions/{run_id}` | Détail complet d'une session |

### Corps des requêtes

```python
# POST /analyse/analyste
{ "sample_size": 200 }

# POST /analyse/veille · /analyse/rejeter · /analyse/redacteur
{ "run_id": "abc12345" }

# POST /analyse/stratege
{ "run_id": "abc12345", "humain_approved": true }   # ⚠ "humain", pas "human"
```

### Codes d'erreur

| Code | Raison |
| --- | --- |
| `400` | Étape précédente non exécutée sur ce `run_id` |
| `403` | `humain_approved: false` sur `/analyse/stratege` |
| `404` | `run_id` inconnu |
| `500` | Corpus non chargé ou agent en échec |

---

## Session store

Les sessions sont persistées dans `outputs/session_{run_id}.json` via écriture atomique.

**Statuts possibles**

| Statut | Condition |
| --- | --- |
| `analyste_done` | `narratives` non null |
| `awaiting_human` | `alerts` non null, `human_approved` false |
| `rejected` | Forcé par `POST /analyse/rejeter` |
| `stratege_done` | `strategy_options` non null |
| `complete` | `draft_response` non null |

`raw_df` et `tweets_sample` sont exclus de la persistance (DataFrames volumineux) — ils sont ré-injectés depuis `df_global` à chaque appel.

**Sécurité** : `run_id` validé par regex `^[A-Za-z0-9_-]{1,64}$` + vérification `resolve()` (protection path traversal).

---

## Règles d'architecture

| Règle | Ce qu'elle interdit |
| --- | --- |
| `load_corpus()` est le seul point d'entrée | Lecture directe de `Dataset/data.xlsx` dans un agent |
| `get_llm()` pour toute instanciation LLM | Clé API en dur, instanciation directe de `ChatGroq` |
| `get_system_prompt()` pour tout prompt système | Prompt système codé en dur dans un fichier agent |
| `source_tweet_ids` requis dans chaque output Pydantic | Claims LLM sans trace vers des `postID` réels |
| `CrisisState` est le seul vecteur entre agents | Variables globales, effets de bord |
