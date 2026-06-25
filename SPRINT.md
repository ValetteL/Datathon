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
pip install -r requirements.txt
```

Sur **Google Colab** (environnement de travail commun) :
1. Ouvrir Colab → monter le Drive → cloner le repo ou uploader les fichiers
2. Aller dans Colab Secrets → ajouter `GOOGLE_API_KEY` (Louis te donne la clé)
3. Télécharger `Dataset/` depuis le Drive partagé (lien fourni par Louis) et le placer à la racine

Vérification :
```python
from tools.corpus_loader import load_corpus
df = load_corpus("Dataset/data.xlsx")
# → doit afficher : 35396 tweets chargés
```

---

## Ce qu'on construit

Un pipeline multi-agents qui analyse la crise virale CNC × Ultia automatiquement :

```
Corpus (35k tweets)
      ↓
AgentAnalyste   → classe chaque tweet par narratif (censure / copinage / ...)  ⬜ TODO — Ruben
      ↓
AgentVeille     → détecte les pics, les tweets viraux, les alertes              ✅ FAIT
      ↓
[Validation humaine obligatoire]
      ↓
AgentStratège   → propose 3 options de réponse institutionnelle                ✅ FAIT — Baptiste
      ↓
AgentRédacteur  → rédige les drafts de communiqué                              ✅ FAIT — Baptiste
      ↓
outputs/        → JSON + drafts prêts pour la démo
```

Architecture complète : [`_bmad-output/architecture/.../PROJET-ARCHITECTURE.md`](_bmad-output/architecture/architecture-datathon-cnc-ultia-2026-06-24/PROJET-ARCHITECTURE.md)

---

## Qui fait quoi

| Personne | J1 — Comprendre | J2 — Prototyper | J3 — Restituer |
|---|---|---|---|
| **Alexis (P1)** | Exploration timeline & volume ✅ | Tests agents sur échantillon | Support run corpus |
| **Franck (P2)** | Exploration sentiments & narratifs | Tests agents + doc méthodo | Slides pitch |
| **Ruben (P3)** | Exploration acteurs & propagation | **AgentAnalyste** ⚡ | Intégration pipeline |
| **Malo (P4)** | Exploration coordination & sémantique | Valider AgentVeille | Run corpus entier |
| **Baptiste (P5)** | — | **AgentStratège ✅ + AgentRédacteur ✅** | Intégration pipeline |
| **Louis** | Synthèse grille 5 axes + slides ✅ | Intégration pipeline complète | HumanGate + démo |

⚡ = Stories bloquantes J2 — AgentAnalyste (Ruben) est le dernier bloc manquant

---

## Livrables attendus

| Jour | Livrable | Responsable |
|---|---|---|
| **J1 soir** | Slides : grille 5 axes + timeline + 2-3 chiffres clé | P5 + Louis |
| **J2 soir** | Agents qui tournent + notebook de démonstration + doc méthodo | Tous |
| **J3** | Démo live orchestrée + pitch 10 min devant jury | Tous |

---

## Règles à respecter (non négociables)

1. **Ne jamais lire `Dataset/` directement** — tout passe par `load_corpus()`
2. **Clé API jamais dans le code** — uniquement `os.environ` ou Colab Secrets
3. **`source_tweet_ids` obligatoire** dans chaque output agent (anti-hallucination)
4. **HumanGate obligatoire** avant la génération de réponses — l'équipe valide ensemble
5. **Ton neutre** — les agents décrivent, ne jugent pas

---

## Suivi de l'avancement (Sprint Status BMAD)

Le fichier [`_bmad-output/implementation-artifacts/sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml) trace l'état de chaque story.

Pour mettre à jour manuellement : édite le statut de ta story dans le YAML.

```yaml
# Exemple : quand tu commences la Story 1.2
1-2-exploration-temporelle-timeline-de-la-crise: in-progress

# Quand c'est terminé
1-2-exploration-temporelle-timeline-de-la-crise: done
```

Statuts disponibles : `backlog` → `in-progress` → `review` → `done`

Pour voir le détail complet de chaque story (tâches, critères de succès) :
→ [`_bmad-output/planning-artifacts/epics.md`](_bmad-output/planning-artifacts/epics.md)

---

## En cas de doute

- Architecture & décisions techniques : [`PROJET-ARCHITECTURE.md`](_bmad-output/architecture/architecture-datathon-cnc-ultia-2026-06-24/PROJET-ARCHITECTURE.md)
- Méthode BMAD & installation : [`GUIDE_BMAD.md`](GUIDE_BMAD.md)
- Code déjà fait (lire avant de recoder) : `agents/veille.py`, `src/agents/stratege.py`, `src/agents/redacteur.py`, `pipeline/graph.py`, `tools/corpus_loader.py`
- Demo interactive : `python src/main.py` (Veille → HumanGate → Stratège → Rédacteur, narratives mockées)
- Rapport J1 + chiffres clés : `docs/RAPPORT_J1.md`, `slides/chiffres_cles.json`
- Chef de projet : Louis
