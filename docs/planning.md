# Sprint planning — Datathon CNC × Ultia

**Équipe : 6 personnes | Stack : Python | Durée : 3 jours**

| Rôle                       | Personnes |
| -------------------------- | --------- |
| Data Analysts (DA)         | P1, P2    |
| Agent Devs (AD)            | P3, P4    |
| Orchestration + Infra (OR) | P5        |
| Slides + Coordination (PM) | P6        |

### Jour 1 — Comprendre

| Tâche                                                     | Qui        | Livrable                          |
| --------------------------------------------------------- | ---------- | --------------------------------- |
| Chargement + nettoyage `data.xlsx` (dates, doublons, NaN) | P1, P2, P3 | DataFrame propre                  |
| Timeline volume par jour + heure (25–30 mars)             | P1         | Graphique timeline + patient zéro |
| Top acteurs (volume + partages), top hashtags             | P2         | Tableaux classements              |
| Répartition sentiment + types d'engagement                | P2         | Chiffres clés                     |
| Setup stack LangChain + clé API + premier agent simple    | P3, P4     | Agent qui tourne sur 100 tweets   |
| Setup Google Colab partagé + structure du repo            | P5         | Environnement commun              |
| Slides J1 (grille 5 axes + timeline + 3 chiffres clés)    | P6         | Slides livrables du soir          |

### Jour 2 — Concevoir & Prototyper

| Tâche                                                          | Qui | Livrable                               |
| -------------------------------------------------------------- | --- | -------------------------------------- |
| Finalisation visualisations (matplotlib/seaborn)               | P1  | Graphiques propres                     |
| Clustering narratifs (censure / copinage / défense)            | P2  | Classification sur échantillon         |
| Agent Analyste (classifie tweet → narratif + acteur)           | P3  | Agent testé sur échantillon 26-27 mars |
| Agent Veille/Alerte (détecte pic + seuil de vitesse)           | P4  | Agent testé sur corpus complet         |
| Agent Stratège/Rédacteur (propose réponse de crise)            | P5  | Agent testé sur 3-4 cas                |
| Vérification manuelle des outputs agents (hallucinations)      | P6  | Rapport de qualité                     |
| Documentation architecture + limites + scalabilité dans slides | P6  | Slides J2 enrichies                    |

### Jour 3 — Orchestrer & Restituer

| Tâche                                                            | Qui    | Livrable              |
| ---------------------------------------------------------------- | ------ | --------------------- |
| Orchestration LangGraph : Analyste → Veille → Stratège/Rédacteur | P3, P5 | Pipeline bout en bout |
| Tests sur corpus complet + mesure temps exécution                | P4     | Rapport de test       |
| Préparation démo live (sous-ensemble replay)                     | P3, P4 | Script de démo        |
| Slides finales (architecture, insights, agents, pitch)           | P6     | Slides finales        |
| Révision globale + répétition pitch (10 min)                     | Tous   | Pitch calé            |

---

## Sprint planning — Par personne

### P1 — Data Analyst · Temporalité & Propagation

**US :** _En tant qu'analyste, je veux cartographier la propagation dans le temps afin d'identifier le patient zéro et les pics de viralité._

| Jour | Tâche                                                   | Livrable                                      |
| ---- | ------------------------------------------------------- | --------------------------------------------- |
| J1   | Chargement + nettoyage `data.xlsx` avec P2/P3           | DataFrame propre, types corrects, NaN traités |
| J1   | Timeline volume par jour (19 mars → 1er mai)            | Graphique volume quotidien annoté             |
| J1   | Zoom horaire 25–30 mars, identification patient zéro    | Graphique horaire + fiche patient zéro        |
| J2   | Timeline sentiment dans le temps (évolution négativité) | Graphique sentiment superposé au volume       |
| J2   | Vitesse de propagation : delta 1er tweet → pic          | Métrique vitesse + interprétation             |
| J3   | Finition graphiques pour la démo                        | 2–3 visuels propres intégrés aux slides       |

### P2 — Data Analyst · Acteurs & Narratifs

**US :** _En tant qu'analyste, je veux identifier qui parle et de quoi afin de comprendre les camps en présence et leur poids réel._

| Jour | Tâche                                                                   | Livrable                                 |
| ---- | ----------------------------------------------------------------------- | ---------------------------------------- |
| J1   | Chargement + nettoyage `data.xlsx` avec P1/P3                           | DataFrame propre                         |
| J1   | Top acteurs par volume de messages                                      | Classement top 20 comptes                |
| J1   | Top acteurs par partages cumulés                                        | Classement top 20 par reach              |
| J1   | Répartition sentiment (neutre/négatif/positif) + types d'engagement     | Chiffres clés (66% neutre, 86% RT, etc.) |
| J1   | Top hashtags (#cnc, #ultia, #racketfiscal…)                             | Fréquences + interprétation              |
| J2   | Clustering narratifs par mots-clés (censure / copinage / défense Ultia) | Table de classification sur échantillon  |
| J2   | Analyse comptes vérifiés vs non vérifiés sur le pic                     | Chiffre clé : 9% vérifiés                |
| J3   | Finition visuels acteurs/narratifs pour slides                          | 2 graphiques propres                     |

### P3 — Agent Dev · Agent Analyste

**US :** _En tant que cellule de crise, je veux qu'un agent classe automatiquement chaque tweet par narratif et type d'acteur afin de gagner du temps sur le tri manuel._

| Jour | Tâche                                                        | Livrable                                   |
| ---- | ------------------------------------------------------------ | ------------------------------------------ |
| J1   | Chargement + nettoyage `data.xlsx` avec P1/P2                | DataFrame propre                           |
| J1   | Setup LangChain + clé API (Gemini/Groq) avec P4              | Stack qui tourne, premier appel LLM validé |
| J2   | Prompt engineering Agent Analyste (narratif + acteur)        | Prompt v1 documenté                        |
| J2   | Test Agent Analyste sur échantillon 26–27 mars (~500 tweets) | Output : table tweet → narratif + acteur   |
| J2   | Vérification manuelle + itération prompt                     | Prompt v2, taux d'erreur estimé            |
| J3   | Intégration Agent Analyste dans le pipeline LangGraph        | Nœud Analyste fonctionnel                  |
| J3   | Test bout en bout + corrections                              | Agent stable sur corpus complet            |

### P4 — Agent Dev · Agent Veille/Alerte

**US :** _En tant que cellule de crise, je veux être alerté automatiquement dès qu'un seuil de propagation est dépassé afin de réagir avant que la crise ne s'emballe._

| Jour | Tâche                                                                              | Livrable                                   |
| ---- | ---------------------------------------------------------------------------------- | ------------------------------------------ |
| J1   | Setup LangChain + clé API avec P3                                                  | Stack commune validée                      |
| J1   | Exploration colonnes utiles à la détection de pics (Date, Shares, Engagement Type) | Note technique sur les colonnes mobilisées |
| J2   | Définition des seuils d'alerte (volume/heure, vitesse de propagation)              | Seuils documentés et justifiés             |
| J2   | Prompt + logique Agent Veille (détecte pic → génère alerte structurée)             | Prompt v1 documenté                        |
| J2   | Test sur corpus historique (simuler une détection sur le 26 mars)                  | Output : alerte structurée générée         |
| J3   | Intégration dans le pipeline + tests corpus complet                                | Nœud Veille fonctionnel                    |
| J3   | Mesure temps d'exécution sur corpus complet                                        | Rapport de performance                     |

### P5 — Orchestration & Infra

**US :** _En tant qu'équipe, je veux un pipeline d'agents qui s'enchaînent automatiquement afin de livrer une démo reproductible sur n'importe quel corpus de crise._

| Jour | Tâche                                                                             | Livrable                            |
| ---- | --------------------------------------------------------------------------------- | ----------------------------------- |
| J1   | Setup Google Colab partagé + structure repo (dossiers, conventions)               | Environnement commun opérationnel   |
| J1   | Centralisation du DataFrame propre accessible à tous                              | Fichier partagé versionné           |
| J2   | Agent Stratège/Rédacteur : prompt + test sur 3–4 cas réels                        | Output : réponses de crise rédigées |
| J2   | Vérification neutralité des outputs (respect de la consigne "décrire sans juger") | Rapport de revue qualité            |
| J3   | Architecture LangGraph : chaîne Analyste → Veille → Stratège/Rédacteur            | Pipeline orchestré bout en bout     |
| J3   | Script de démo (replay sur sous-ensemble corpus)                                  | Script démo prêt à jouer live       |

### P6 — Coordination & Slides

**US :** _En tant que jury, je veux comprendre l'analyse et la valeur des agents en 10 minutes afin d'évaluer la pertinence de la solution pour une cellule de crise._

| Jour | Tâche                                                                    | Livrable                |
| ---- | ------------------------------------------------------------------------ | ----------------------- |
| J1   | Grille 5 axes remplie à partir des premières analyses                    | Grille documentée       |
| J1   | Slides J1 : grille + timeline + 3 chiffres clés                          | Slides livrable du soir |
| J2   | Vérification manuelle outputs agents (hallucinations, biais, neutralité) | Rapport qualité         |
| J2   | Slides J2 : architecture agents, limites, scalabilité                    | Slides enrichies        |
| J3   | Slides finales : analyse + agents + architecture + pitch                 | Slides finales          |
| J3   | Coordination répétition pitch (timing 10 min, répartition parole)        | Pitch calé, minuté      |
