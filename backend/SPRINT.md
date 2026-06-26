# Brief Sprint — Datathon CNC × Ultia

> Datathon NEXA Digital School — Équipe de 6
> Chef de projet : Louis

Tout le code, l'architecture et le sprint planning sont déjà dans le repo.
**Lis ce fichier, clone, et tu sais quoi faire dès J1 matin.**

---

## Setup (15 min — à faire avant J1)

```bash
git clone https://github.com/myaifactory-sketch/Datathon.git
cd Datathon
```

**Backend :**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # ajouter GROQ_API_KEY ou GOOGLE_API_KEY
uvicorn main:app --reload --port 8000
```

**Frontend :**
```bash
cd frontend
pnpm install
pnpm dev
```

Sur **Google Colab** (pour les notebooks) :
1. Ouvrir Colab → monter le Drive → cloner le repo
2. Colab Secrets → ajouter `GOOGLE_API_KEY` (Louis te donne la clé)
3. Télécharger `Dataset/` depuis le Drive partagé et le placer dans `backend/Dataset/`

Vérification corpus :
```python
import sys; sys.path.insert(0, "src")
from tools.corpus_loader import load_corpus
df = load_corpus("Dataset/data.xlsx")
# → doit afficher : 35396 tweets chargés
```

---

## Ce qu'on construit

Un pipeline multi-agents + interface React qui analyse la crise virale CNC × Ultia automatiquement :

```
Corpus (35k tweets)
      ↓
AgentAnalyste   → classe chaque tweet par narratif (censure / copinage / …)  ✅ FAIT
      ↓
AgentVeille     → détecte les pics, les tweets viraux, les alertes            ✅ FAIT
      ↓
[Validation humaine obligatoire — interface React]
      ↓
AgentStratège   → propose 3 options de réponse institutionnelle               ✅ FAIT — Baptiste
      ↓
AgentRédacteur  → rédige les drafts de communiqué                            ✅ FAIT — Baptiste
      ↓
outputs/        → sessions JSON persistées, reprises depuis le front
```

API FastAPI : http://localhost:8000 | Swagger : http://localhost:8000/docs  
Interface React : http://localhost:5173

---

## Qui fait quoi

| Personne | J1 — Comprendre | J2 — Prototyper | J3 — Restituer |
|---|---|---|---|
| **Alexis (P1)** | Exploration timeline & volume ✅ | Tests agents sur échantillon | Support run corpus |
| **Franck (P2)** | Exploration sentiments & narratifs | Tests agents + doc méthodo | Slides pitch |
| **Ruben (P3)** | Exploration acteurs & propagation | **AgentAnalyste ✅** | Intégration pipeline |
| **Malo (P4)** | Exploration coordination & sémantique | Valider AgentVeille | Run corpus entier |
| **Baptiste (P5)** | — | **AgentStratège ✅ + AgentRédacteur ✅ + API FastAPI ✅ + Frontend ✅** | Intégration |
| **Louis** | Synthèse grille 5 axes + slides ✅ | Intégration pipeline complète | HumanGate + démo |

---

## Livrables attendus

| Jour | Livrable | Responsable |
|---|---|---|
| **J1 soir** | Slides : grille 5 axes + timeline + 2-3 chiffres clé | P5 + Louis |
| **J2 soir** | Pipeline complet qui tourne + interface React + doc méthodo | Tous |
| **J3** | Démo live orchestrée + pitch 10 min devant jury | Tous |

---

## Règles à respecter (non négociables)

1. **Ne jamais lire `Dataset/` directement** — tout passe par `load_corpus()`
2. **Clé API jamais dans le code** — uniquement `os.environ` ou `.env`
3. **`source_tweet_ids` obligatoire** dans chaque output agent (anti-hallucination)
4. **HumanGate obligatoire** avant la génération de réponses — l'équipe valide ensemble
5. **Ton neutre** — les agents décrivent, ne jugent pas

---

## Ce qui reste à faire (J3)

| Tâche | Responsable | Priorité |
|---|---|---|
| Run complet sur corpus entier (1000-2000 tweets) | P3 + P4 | HAUTE |
| Valider taxonomie narratifs (Analyste) avec exemples P2 | Franck + Ruben | HAUTE |
| Enrichir few-shot dans `src/agents/analyste.py` | Ruben | MOYENNE |
| Finaliser `slides/chiffres_cles.json` (narratif_dominant, top_acteur_type, terme_dominant) | Franck + Ruben + Malo | HAUTE |
| Finaliser slides pitch (10 slides avec vrais chiffres) | P2 + Louis | HAUTE |
| Répétition démo live + plan B (outputs JSON pré-sauvegardés) | Toute l'équipe | HAUTE |

---

## Suivi de l'avancement

Le fichier [`_bmad-output/implementation-artifacts/sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml) trace l'état de chaque story.

Statuts : `backlog` → `in-progress` → `review` → `done`

---

## En cas de doute

- Architecture & décisions techniques : [`_bmad-output/architecture/.../PROJET-ARCHITECTURE.md`](_bmad-output/architecture/architecture-datathon-cnc-ultia-2026-06-24/PROJET-ARCHITECTURE.md)
- API complète : `backend/TODO.md` (endpoints, schémas, session store)
- Frontend : `frontend/TODO.md` (composants, machine d'états, appels API)
- Code agents (lire avant de modifier) : `backend/src/agents/`
- Rapport J1 + chiffres clés : `docs/RAPPORT_J1.md`, `slides/chiffres_cles.json`
- Chef de projet : Louis
