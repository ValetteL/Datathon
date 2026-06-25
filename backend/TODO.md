# Backend — Datathon CNC × Ultia

API FastAPI qui expose le pipeline multi-agents d'analyse de crise virale.

## Stack

- Python 3.10+
- FastAPI
- Uvicorn
- LangChain + LangGraph
- Groq (LLM)
- Pydantic v2

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn langchain langchain-groq langgraph pandas openpyxl pydantic
```

## Configuration

```bash
export GROQ_API_KEY="ta_clé"
```

## Lancer le serveur

```bash
uvicorn backend.main:app --reload --port 8000
```

---

## Architecture

```
backend/
├── main.py                  ← FastAPI app + routes
├── agents/
│   ├── veille.py
│   ├── stratege.py
│   └── redacteur.py
├── pipeline/
│   ├── state.py             ← CrisisState TypedDict
│   └── session_store.py     ← stockage des states en mémoire par run_id
├── tools/
│   └── corpus_loader.py
├── prompts/
│   └── prompts.py
├── schemas/
│   ├── requests.py          ← schémas des body de requêtes
│   └── responses.py         ← schémas des réponses API
├── requirements.txt
└── README.md
```

---

## Schémas de données

### Requêtes

```python
# schemas/requests.py

class VeilleRequest(BaseModel):
    sample_size: int = 200
    corpus_config: dict = {
        "evenement": "Affaire Ultia x CNC",
        "periode": "mars-avril 2026"
    }
    narratives_mock: dict | None = None

class StrategeRequest(BaseModel):
    run_id: str
    human_approved: bool

class RedacteurRequest(BaseModel):
    run_id: str
```

### Réponses

```python
# schemas/responses.py

class PeakResponse(BaseModel):
    date: str
    tweet_count: int
    top_shares: int
    source_tweet_ids: list[str]

class VeilleResponse(BaseModel):
    run_id: str
    is_alert: bool
    alert_level: str
    peaks: list[PeakResponse]
    summary: str
    threshold_breaches: dict
    is_mock: bool

class ResponseOptionResponse(BaseModel):
    option_id: str
    titre: str
    description: str
    tonalite: str
    risques: list[str]
    source_tweet_ids: list[str]

class StrategeResponse(BaseModel):
    run_id: str
    options: list[ResponseOptionResponse]
    option_recommandee: str
    justification: str

class DraftVersionResponse(BaseModel):
    tonalite: str
    titre: str
    corps: str
    call_to_action: str
    source_tweet_ids: list[str]

class RedacteurResponse(BaseModel):
    run_id: str
    versions: list[DraftVersionResponse]
    recommandation: str
```

---

## Endpoints

### POST /analyse/veille

Lance l'AgentVeille sur le corpus.

**Body**

```json
{
  "sample_size": 200,
  "corpus_config": {
    "evenement": "Affaire Ultia x CNC",
    "periode": "mars-avril 2026"
  },
  "narratives_mock": null
}
```

**Response**

```json
{
  "run_id": "abc12345",
  "is_alert": true,
  "alert_level": "high",
  "peaks": [...],
  "summary": "...",
  "threshold_breaches": {...},
  "is_mock": false
}
```

---

### POST /analyse/stratege

Lance l'AgentStratège. Nécessite un `run_id` valide issu de la Veille.

**Body**

```json
{
  "run_id": "abc12345",
  "human_approved": true
}
```

**Response**

```json
{
  "run_id": "abc12345",
  "options": [...],
  "option_recommandee": "option2",
  "justification": "..."
}
```

**Erreurs**

- `404` — `run_id` inconnu
- `403` — `human_approved` est `false`

---

### POST /analyse/redacteur

Lance l'AgentRédacteur. Nécessite que le Stratège ait tourné.

**Body**

```json
{
  "run_id": "abc12345"
}
```

**Response**

```json
{
  "run_id": "abc12345",
  "versions": [...],
  "recommandation": "equilibre"
}
```

**Erreurs**

- `404` — `run_id` inconnu
- `400` — Stratège non exécuté sur ce `run_id`

--

### GET /sessions

Retourne la liste de toutes les sessions en mémoire.

**Response**

```json
[
  {
    "run_id": "abc12345",
    "status": "complete",
    "alert_level": "high",
    "created_at": "2026-06-25T09:32:00"
  },
  {
    "run_id": "def67890",
    "status": "awaiting_human",
    "alert_level": "medium",
    "created_at": "2026-06-25T10:15:00"
  }
]
```

---

### GET /sessions/{run_id}

Retourne l'état complet d'une session existante.

**Response**

```json
{
  "run_id": "abc12345",
  "status": "complete",
  "is_mock": false,
  "alerts": {...},
  "strategy_options": {...},
  "draft_response": {...}
}
```

**Erreurs**

- `404` — `run_id` inconnu

---

## User Stories

---

### US-B01 — Initialiser le serveur et le corpus

**En tant que** développeur,
**je veux** que le corpus soit chargé une seule fois au démarrage du serveur,
**afin d'** éviter de recharger le fichier xlsx à chaque requête.

**Tâches**

- Créer `main.py` avec l'app FastAPI
- Charger le corpus au démarrage via `lifespan` FastAPI
- Stocker le DataFrame en variable globale accessible par les routes
- Activer CORS pour `http://localhost:5173`

**Critères d'acceptance**

- Le corpus est chargé une seule fois au démarrage
- Les routes ont accès au DataFrame sans le recharger
- CORS configuré pour le front React

**DOD**

- [ ] `load_corpus()` appelé dans `lifespan`
- [ ] DataFrame accessible globalement dans `main.py`
- [ ] CORS activé pour `localhost:5173`
- [ ] Message de confirmation au démarrage : `35396 tweets chargés`

---

### US-B02 — Session store en mémoire

**En tant que** développeur,
**je veux** stocker les states du pipeline par `run_id`,
**afin de** permettre au front d'enchaîner les appels sans renvoyer toutes les données.

**Tâches**

- Créer `pipeline/session_store.py`
- Implémenter `save_state(run_id, state)` et `get_state(run_id)`
- Utiliser un simple dict Python en mémoire
- Lever une `KeyError` si `run_id` inconnu

**Critères d'acceptance**

- Un state sauvegardé est récupérable par son `run_id`
- Un `run_id` inconnu lève une erreur propre
- Pas de dépendance externe (pas de Redis, pas de DB)

**DOD**

- [ ] `save_state` et `get_state` implémentés
- [ ] Dict en mémoire utilisé comme store
- [ ] `KeyError` levée si `run_id` inconnu
- [ ] Store importable depuis `main.py`

---

### US-B03 — Route POST /analyse/veille

**En tant que** frontend,
**je veux** appeler la Veille et recevoir les résultats structurés,
**afin d'** afficher l'état de la crise à l'opérateur.

**Tâches**

- Créer la route `POST /analyse/veille` dans `main.py`
- Générer un `run_id` unique (UUID court)
- Initialiser un `CrisisState` avec le corpus et le `corpus_config`
- Injecter `narratives_mock` si fourni dans le body
- Appeler `run_veille(state)`
- Sauvegarder le state dans le session store
- Retourner un `VeilleResponse` avec `is_mock: true/false`

**Critères d'acceptance**

- La route répond en moins de 30 secondes
- Le `run_id` est unique et retourné dans la réponse
- `is_mock` est `true` si `narratives_mock` fourni
- Le state est bien sauvegardé pour les appels suivants

**DOD**

- [ ] Route créée et documentée dans Swagger (`/docs`)
- [ ] `run_id` généré et retourné
- [ ] `run_veille` appelé avec le bon state
- [ ] State sauvegardé dans le session store
- [ ] `is_mock` correctement renseigné
- [ ] Réponse validée par `VeilleResponse`

---

### US-B04 — Route POST /analyse/stratege

**En tant que** frontend,
**je veux** appeler le Stratège après validation humaine,
**afin d'** obtenir les options de réponse institutionnelle.

**Tâches**

- Créer la route `POST /analyse/stratege` dans `main.py`
- Récupérer le state depuis le session store via `run_id`
- Retourner `403` si `human_approved` est `false`
- Mettre `state["human_approved"] = True`
- Appeler `run_stratege(state)`
- Mettre à jour le state dans le session store
- Retourner un `StrategeResponse`

**Critères d'acceptance**

- `403` retourné si `human_approved: false`
- `404` retourné si `run_id` inconnu
- Le state est mis à jour après l'appel
- La réponse contient les 3 options avec leurs risques

**DOD**

- [ ] Route créée et documentée dans Swagger
- [ ] `404` si `run_id` inconnu
- [ ] `403` si `human_approved: false`
- [ ] `run_stratege` appelé avec le bon state
- [ ] State mis à jour dans le session store
- [ ] Réponse validée par `StrategeResponse`

---

### US-B05 — Route POST /analyse/redacteur

**En tant que** frontend,
**je veux** appeler le Rédacteur après le Stratège,
**afin d'** obtenir les drafts de communiqué.

**Tâches**

- Créer la route `POST /analyse/redacteur` dans `main.py`
- Récupérer le state depuis le session store via `run_id`
- Retourner `400` si `strategy_options` est `None` dans le state
- Appeler `run_redacteur(state)`
- Mettre à jour le state dans le session store
- Retourner un `RedacteurResponse`

**Critères d'acceptance**

- `404` retourné si `run_id` inconnu
- `400` retourné si le Stratège n'a pas encore tourné
- La réponse contient les 3 versions avec call to action
- La version recommandée est identifiée

**DOD**

- [ ] Route créée et documentée dans Swagger
- [ ] `404` si `run_id` inconnu
- [ ] `400` si `strategy_options` est `None`
- [ ] `run_redacteur` appelé avec le bon state
- [ ] State mis à jour dans le session store
- [ ] Réponse validée par `RedacteurResponse`

---

### US-B06 — Gestion des erreurs globale

**En tant que** frontend,
**je veux** recevoir des erreurs structurées et lisibles,
**afin d'** afficher un message clair à l'opérateur.

**Tâches**

- Ajouter un `exception_handler` global dans `main.py`
- Format d'erreur uniforme : `{"error": "message", "detail": "..."}`
- Gérer les cas : `run_id` inconnu, `human_approved` false, agent qui plante

**Critères d'acceptance**

- Toutes les erreurs retournent le même format JSON
- Les codes HTTP sont corrects (400, 403, 404, 500)
- Les erreurs LLM (timeout, quota) sont catchées et retournent un 500 lisible

**DOD**

- [ ] Exception handler global ajouté
- [ ] Format `{"error": "...", "detail": "..."}` sur toutes les erreurs
- [ ] Erreurs LangChain catchées et transformées en 500
- [ ] Codes HTTP corrects sur toutes les routes

---

### US-B07 — Lister les sessions existantes

**En tant que** opérateur,
**je veux** voir la liste des sessions précédentes,
**afin de** reprendre une analyse sans relancer le pipeline.

**Tâches**

- Ajouter `created_at` et `status` dans le session store à chaque sauvegarde
- Créer la route `GET /sessions`
- Calculer le `status` depuis l'état du state :
  - `veille_done` si `alerts` non null et `human_approved` false
  - `awaiting_human` si `alerts` non null et `human_approved` false et pas de rejet
  - `rejected` si `human_approved` explicitement rejeté
  - `stratege_done` si `strategy_options` non null
  - `complete` si `draft_response` non null
- Retourner la liste triée par `created_at` décroissant

**Critères d'acceptance**

- La liste est triée de la plus récente à la plus ancienne
- Le `status` reflète fidèlement l'état réel du pipeline
- Une session vide (Veille non encore lancée) n'apparaît pas

**DOD**

- [ ] `created_at` ajouté dans le session store
- [ ] `status` calculé correctement depuis le state
- [ ] Route `GET /sessions` créée et documentée
- [ ] Liste triée par `created_at` décroissant
- [ ] Sessions sans `alerts` exclues de la liste

---

### US-B08 — Récupérer une session par run_id

**En tant que** opérateur,
**je veux** récupérer l'état complet d'une session passée,
**afin de** reprendre le pipeline là où il s'était arrêté ou revoir les résultats.

**Tâches**

- Créer la route `GET /sessions/{run_id}`
- Récupérer le state depuis le session store
- Retourner tous les outputs disponibles (`alerts`, `strategy_options`, `draft_response`)
- Inclure `status` et `is_mock`

**Critères d'acceptance**

- `404` si `run_id` inconnu
- Tous les outputs disponibles sont retournés
- Le front peut reprendre le pipeline depuis le bon état

**DOD**

- [ ] Route créée et documentée dans Swagger
- [ ] `404` si `run_id` inconnu
- [ ] `alerts`, `strategy_options`, `draft_response` retournés si disponibles
- [ ] `status` et `is_mock` inclus dans la réponse

---

## Ordre d'implémentation recommandé

1. `schemas/requests.py` + `schemas/responses.py`
2. `pipeline/session_store.py` (US-B02)
3. `main.py` — app FastAPI + CORS + lifespan (US-B01)
4. `POST /analyse/veille` (US-B03)
5. `POST /analyse/stratege` (US-B04)
6. `POST /analyse/redacteur` (US-B05)
7. Gestion des erreurs globale (US-B06)

```

```
