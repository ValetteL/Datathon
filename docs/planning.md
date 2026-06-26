# Planning sprint — Datathon CNC × Ultia

**Équipe : 6 personnes | Stack : Python + React | Durée : 3 jours**

| Rôle | Personnes |
| --- | --- |
| Data Analysts | Alexis (P1), Franck (P2) |
| Agent Devs | Ruben (P3), Malo (P4) |
| Orchestration + Frontend | Baptiste (P5) |
| Coordination + Slides | Louis |

---

## Jour 1 — Comprendre ✅

| Tâche | Qui | Statut |
| --- | --- | --- |
| Chargement + nettoyage `data.xlsx` | P1, P2, P3 | ✅ |
| Timeline volume par jour/heure (25–30 mars) | P1 | ✅ |
| Top acteurs, hashtags, répartition sentiment | P2 | ✅ |
| Setup stack LangChain + clé API | P3, P4 | ✅ |
| Setup repo + environnement commun | P5 | ✅ |
| Slides J1 (grille 5 axes + 3 chiffres clés) | Louis | ✅ |

**Livrables J1** : `slides/figures/fig_timeline.png`, `slides/chiffres_cles.json` (métriques Louis), `docs/RAPPORT_J1.md`

---

## Jour 2 — Concevoir & Prototyper ✅

| Tâche | Qui | Statut |
| --- | --- | --- |
| AgentAnalyste — classification narratifs + acteurs | Ruben | ✅ |
| AgentVeille — détection pics + alertes | Malo | ✅ |
| AgentStratège — options de réponse institutionnelle | Baptiste | ✅ |
| AgentRédacteur — rédaction communiqués | Baptiste | ✅ |
| API FastAPI (tous les endpoints) | Baptiste | ✅ |
| Interface React complète | Baptiste | ✅ |
| Vérification manuelle outputs agents | Louis | ✅ |

**Livrables J2** : pipeline complet Analyste → Veille → HumanGate → Stratège → Rédacteur, interface React avec sessions persistées.

---

## Jour 3 — Orchestrer & Restituer

| Tâche | Qui | Priorité |
| --- | --- | --- |
| Run complet sur corpus entier (1 000–2 000 tweets) | P3 + P4 | 🔴 HAUTE |
| Valider taxonomie narratifs (AgentAnalyste) avec exemples P2 | Franck + Ruben | 🔴 HAUTE |
| Enrichir few-shot dans `src/agents/analyste.py` | Ruben | 🟡 MOYENNE |
| Finaliser `slides/chiffres_cles.json` (champs manquants) | Franck + Ruben + Malo | 🔴 HAUTE |
| Slides finales (10 slides avec vrais chiffres et vrais outputs) | Franck + Louis | 🔴 HAUTE |
| Répétition démo live + plan B (outputs JSON pré-sauvegardés) | Tous | 🔴 HAUTE |

**Champs manquants dans `slides/chiffres_cles.json`** :

| Champ | Responsable |
| --- | --- |
| `narratif_dominant` | Franck |
| `terme_dominant` | Franck |
| `top_acteur_type` | Ruben |
| `note_coordination` | Malo |

---

## Planning par personne

### P1 — Alexis · Temporalité & Propagation

| Jour | Tâche | Statut |
| --- | --- | --- |
| J1 | Chargement + nettoyage corpus | ✅ |
| J1 | Timeline volume par jour (19 mars → 1er mai) | ✅ |
| J1 | Zoom horaire 25–30 mars, patient zéro | ✅ |
| J2 | Tests agents sur échantillon | ✅ |
| J3 | Support run corpus entier + finition graphiques | ⬜ |

### P2 — Franck · Narratifs & Sémantique

| Jour | Tâche | Statut |
| --- | --- | --- |
| J1 | Top acteurs, hashtags, sentiment | ✅ |
| J2 | Clustering narratifs + few-shot examples pour AgentAnalyste | ✅ |
| J3 | Renseigner `narratif_dominant` + `terme_dominant` dans JSON | ⬜ |
| J3 | Slides finales | ⬜ |

### P3 — Ruben · Acteurs & AgentAnalyste

| Jour | Tâche | Statut |
| --- | --- | --- |
| J1 | Exploration acteurs + propagation | ✅ |
| J2 | Implémenter `src/agents/analyste.py` | ✅ |
| J3 | Renseigner `top_acteur_type` dans JSON | ⬜ |
| J3 | Valider AgentAnalyste sur vrais tweets avec clé API | ⬜ |
| J3 | Run complet corpus | ⬜ |

### P4 — Malo · Coordination & AgentVeille

| Jour | Tâche | Statut |
| --- | --- | --- |
| J1 | Exploration coordination + sémantique | ✅ |
| J2 | Valider AgentVeille sur corpus réel, ajuster seuils | ✅ |
| J3 | Renseigner `note_coordination` dans JSON | ⬜ |
| J3 | Run corpus entier + rapport performance | ⬜ |

### P5 — Baptiste · Orchestration & Frontend

| Jour | Tâche | Statut |
| --- | --- | --- |
| J2 | AgentStratège + AgentRédacteur | ✅ |
| J2 | API FastAPI complète (7 endpoints) | ✅ |
| J2 | Interface React (pipeline + sessions + CollapsibleCard) | ✅ |
| J3 | Support intégration pipeline | ⬜ |

### Louis · Chef de projet & Intégration

| Jour | Tâche | Statut |
| --- | --- | --- |
| J1 | Synthèse grille 5 axes + slides J1 + notebook EDA | ✅ |
| J2 | Vérification manuelle outputs agents | ✅ |
| J3 | Intégration pipeline end-to-end | ⬜ |
| J3 | Slides finales + coordination répétition pitch (10 min) | ⬜ |
