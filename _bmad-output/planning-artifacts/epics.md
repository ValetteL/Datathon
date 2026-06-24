# Epics — Datathon CNC × Ultia
# Équipe : 6 × Chef de projet data/IA
# Contrainte : 3 jours (J1/J2/J3) — Google Colab partagé — LangGraph + Gemini 2.0 Flash

> Référence architecture : `_bmad-output/architecture/architecture-datathon-cnc-ultia-2026-06-24/PROJET-ARCHITECTURE.md`
> Contrats techniques (AD-1 à AD-10) sont **non-négociables** — lire avant de coder.

---

## Epic 1: J1 — Comprendre la crise (Exploration corpus)

**Objectif** : Produire une lecture partagée du corpus (35 396 tweets) et une grille d'analyse sur les 5 axes.
**Livrable** : Slides — grille 5 axes + timeline + 2-3 chiffres clé.
**Date cible** : Jour 1

### Story 1.1: Setup environnement et prise en main du repo

**Responsable** : Toute l'équipe (30 min en début de J1)
**Critère de succès** : Chaque membre peut lancer `load_corpus()` dans Colab et voir `35396 tweets chargés`.

Tâches :
- Cloner le repo + `pip install -r requirements.txt`
- Suivre `GUIDE_BMAD.md` section "Setup en 3 minutes"
- Configurer `GOOGLE_API_KEY` dans Colab Secrets
- Vérifier : `from tools.corpus_loader import load_corpus; df = load_corpus()`
- Ouvrir `_bmad-output/architecture/.../PROJET-ARCHITECTURE.md` — lire sections 1-4

### Story 1.2: Exploration temporelle — timeline de la crise

**Responsable** : P1
**Critère de succès** : Graphique volume/heure avec annotation des événements clés identifiés.

Tâches :
- Courbe tweets/heure sur toute la période (19 mars → 1er mai)
- Identifier les 3-5 pics majeurs et les dater précisément
- Annoter : quel événement réel correspond à chaque pic ? (tweet CNC, article de presse, etc.)
- Calculer : durée totale de la crise, vitesse de montée, vitesse de descente
- Livrable intermédiaire : 1 graphique + tableau des pics annotés

### Story 1.3: Exploration sentiments et narratifs

**Responsable** : P2
**Critère de succès** : Répartition sentiment + identification des 3-5 narratifs dominants avec exemples de tweets.

Tâches :
- Distribution sentiment (positive/negative/neutral) sur l'ensemble du corpus
- Évolution du sentiment par jour (stacked bar ou area chart)
- Lire manuellement 50-80 tweets par narratif pressenti (censure / copinage / cyberharcèlement / soutien Ultia / soutien CNC)
- Proposer une taxonomie de 4-6 narratifs pour l'AgentAnalyste
- Exemples de tweets représentatifs pour chaque narratif (→ alimentera les prompts J2)

### Story 1.4: Exploration acteurs et propagation

**Responsable** : P3
**Critère de succès** : Identification des top 20 comptes influents + répartition par type d'acteur.

Tâches :
- Répartition par Engagement Type (RETWEET / REPLY / QUOTE / ORIGINAL)
- Top 20 comptes par volume de tweets, puis par Shares reçus
- Classifier manuellement ces 20 comptes : media / influenceur / institution / militant / anonyme
- Identifier les "tweets seeds" (ceux qui ont déclenché les vagues) via postID + X Repost of
- Vérifier la distribution X Verified vs non-vérifiés dans les top comptes

### Story 1.5: Exploration coordination et sémantique

**Responsable** : P4
**Critère de succès** : Indicateurs de coordination automatisée + analyse du vocabulaire dominant.

Tâches :
- Détecter les rafales (>10 tweets identiques en <5 min) → signe de copier-coller ou bot
- Analyser la synchronie : tweets simultanés avec même hashtag ou mention
- Extraire les 30 termes/expressions les plus fréquents par jour (word frequency sur message_normalizer)
- Repérer les glissements sémantiques : vocabulaire J1-crise vs J3-crise
- Comptes récents (<30 jours) dans les pics → signe de création opportuniste

### Story 1.6: Synthèse grille 5 axes + slides J1

**Responsable** : P5 + P6 (Louis)
**Critère de succès** : Slides prêts pour présentation jury le soir de J1.

Tâches :
- Agréger les livrables P1-P4 dans une grille unique (5 axes : Acteurs / Narratifs / Propagation / Coordination / Sémantique)
- Sélectionner les 2-3 chiffres clés les plus frappants pour le slide de titre
- Construire la timeline visuelle annotée (reprend Story 1.2)
- Formuler les 3 questions que les agents J2 devront répondre (→ brief pour l'équipe)
- Préparer la structure du pitch J3 (plan en 5 slides)

---

## Epic 2: J2 — Concevoir et prototyper les agents

**Objectif** : Implémenter les 3 agents manquants, tester sur échantillon, documenter la méthodo.
**Livrable** : Agents produisant des outputs pertinents + méthodo et explication des agents.
**Date cible** : Jour 2

> ⚠️ AgentVeille (`agents/veille.py`) est **déjà implémenté** — partir de ce fichier comme référence de pattern.

### Story 2.1: Implémenter AgentAnalyste

**Responsable** : P3
**Critère de succès** : `run_analyste(state)` retourne un `NarrativeResult` valide avec `repartition` cohérente sur l'échantillon de 500 tweets.

Tâches :
- Créer `agents/analyste.py` (stub dans `PROJET-ARCHITECTURE.md` §5.2)
- Utiliser la taxonomie narratifs définie en Story 1.3 (P2 fourni les exemples)
- Prompt : inclure 1-2 exemples par narratif (few-shot) pour calibrer le LLM
- Tester sur `df.sample(50)` d'abord, puis sur `tweets_sample` (500 tweets)
- Vérifier : `result.source_tweet_ids` non vide (AD-5 anti-hallucination)
- Ajouter `agents/analyste.py` dans les imports de `pipeline/graph.py`

### Story 2.2: Valider et calibrer AgentVeille sur le corpus réel

**Responsable** : P4
**Critère de succès** : `run_veille(state)` produit un `AlertSignal` avec `alert_level="critical"` et identifie le pic du 27 mars (7303 tweets/jour).

Tâches :
- Charger `agents/veille.py` (déjà implémenté) et lancer sur le corpus complet
- Vérifier que `VOLUME_ALERT_PER_DAY = 2000` déclenche bien l'alerte
- Vérifier que `VIRAL_LIKES_THRESHOLD = 50` identifie les bons tweets seeds (croiser avec Story 1.4)
- Ajuster les seuils si nécessaire (modifier les constantes en haut du fichier)
- Documenter : quels tweets sont identifiés comme viraux ? Cohérent avec l'exploration manuelle ?
- Vérifier l'output JSON dans `outputs/alerts_<run_id>.json`

### Story 2.3: Implémenter AgentStratège

**Responsable** : P5
**Critère de succès** : `run_stratege(state)` retourne 3 options de réponse institutionnelle avec risques/avantages, basées sur le `NarrativeResult` de l'AgentAnalyste.

Tâches :
- Créer `agents/stratege.py` (stub dans `PROJET-ARCHITECTURE.md` §5.5)
- Input : `state["narratives"]` + `state["alerts"]` + `state["corpus_config"]`
- Output Pydantic : `StrategyOptions` avec liste d'options (nom, description, avantages, risques, source_tweet_ids)
- 3 options types : (1) Silence total, (2) Réponse factuelle brève, (3) Dialogue ouvert
- Vérifier : chaque option porte des `source_tweet_ids` justifiant le diagnostic (AD-5)
- Vérifier : `assert state["human_approved"]` en début de fonction (AD-7)

### Story 2.4: Implémenter AgentRédacteur

**Responsable** : P5 (ou P6 si charge trop lourde)
**Critère de succès** : `run_redacteur(state)` produit 3 drafts de communiqué (prudent / équilibré / assertif), chacun <280 caractères pour le format X.

Tâches :
- Créer `agents/redacteur.py` (stub dans `PROJET-ARCHITECTURE.md` §5.6)
- Input : `state["strategy_options"]` + `state["narratives"]`
- Output Pydantic : `DraftCommunique` avec 3 versions + tonalité + source_tweet_ids
- Contraintes éditoriales : NEUTRALITY_SYSTEM_PROMPT obligatoire (AD-4), faits uniquement
- Tester : les drafts ne prennent pas parti politiquement (relecture humaine obligatoire)
- Sauvegarder dans `outputs/drafts_<run_id>.json`

### Story 2.5: Tests agents sur échantillon et documentation méthodo

**Responsable** : P1 + P2
**Critère de succès** : Un notebook `notebooks/J2_tests_agents.ipynb` tourne de bout en bout sur un échantillon de 100 tweets sans erreur.

Tâches :
- Créer `notebooks/J2_tests_agents.ipynb`
- Tester chaque agent isolément (appels directs `run_analyste`, `run_veille`, etc.)
- Documenter les outputs : que produit concrètement chaque agent ? Pertinent ?
- Identifier et logger les erreurs (field `state["errors"]`)
- Rédiger la section "Méthodo agents" pour le livrable J2 (1 page max par agent)
- Préparer les exemples de sorties pour les slides de démo J3

### Story 2.6: Intégration pipeline — premier run complet

**Responsable** : P6 (Louis) + P3
**Critère de succès** : `pipeline/graph.py` tourne de bout en bout (avec HumanGate validé manuellement) sur l'échantillon 500 tweets.

Tâches :
- Connecter tous les agents dans `build_graph()` de `pipeline/graph.py`
- Remplacer les `raise NotImplementedError` par les vrais imports
- Lancer `app.invoke(state)` sur `tweets_sample`
- Valider manuellement au HumanGate : l'analyse est-elle cohérente ?
- Vérifier que `outputs/` contient les 4 fichiers JSON (narratives, alerts, strategy, drafts)
- Débugger les erreurs éventuelles de sérialisation Pydantic → dict

---

## Epic 3: J3 — Orchestrer et restituer

**Objectif** : Pipeline complet sur corpus entier, démo jury, pitch final.
**Livrable** : Démo orchestrée + restitution + pitch 10 min.
**Date cible** : Jour 3

### Story 3.1: Run complet sur corpus entier (35 396 tweets)

**Responsable** : P3 + P4
**Critère de succès** : Pipeline tourne end-to-end sur le corpus complet, outputs JSON cohérents et non-vides.

Tâches :
- Remplacer `tweets_sample` par un échantillon stratifié représentatif (~1000-2000 tweets)
- Gérer les timeouts Gemini (retry avec backoff sur erreur 429)
- Chronométrer chaque nœud : AgentAnalyste < 5 min, AgentVeille < 30 sec
- Vérifier la cohérence des résultats : narrative dominant cohérent avec exploration J1 ?
- Sauvegarder les outputs finaux dans `outputs/` (fichiers datés pour la démo)
- Préparer le run "live" pour la démo (avoir un état sauvegardé si Colab plante)

### Story 3.2: Validation HumanGate et ajustements finaux

**Responsable** : Louis + toute l'équipe
**Critère de succès** : L'équipe valide collectivement le `NarrativeResult` et l'`AlertSignal` avant de passer à la génération de réponses.

Tâches :
- Lancer le pipeline jusqu'au HumanGate
- Présenter l'analyse à l'équipe : narratif dominant, alertes, pics
- Comparer avec l'exploration manuelle J1 : les agents ont-ils trouvé la même chose ?
- Décider : valider ou ajuster les paramètres (seuils, taxonomie narratifs)
- Approuver et lancer la suite : AgentStratège + AgentRédacteur
- Logger la décision dans un commentaire de notebook

### Story 3.3: Finalisation slides et narration pitch

**Responsable** : P2 + P6 (Louis)
**Critère de succès** : Deck de 10 slides prêt, incluant les outputs réels des agents (pas des mockups).

Tâches :
- Structure du pitch : Contexte (1) → Méthodologie (2) → Résultats analyse (3) → Agents (4) → Demo live (5) → Scalabilité (6) → Questions
- Intégrer les vrais chiffres du corpus (depuis Story 1.1-1.5)
- Intégrer les vrais outputs agents (depuis Story 3.1)
- Préparer le script de démo live : quel écran montrer, qui parle, timing
- Anticiper les questions jury : limites, biais, généralisation à d'autres crises

### Story 3.4: Répétition démo et démo finale

**Responsable** : Toute l'équipe
**Critère de succès** : Démo live tourne sans accroc en <10 min devant le jury.

Tâches :
- Répétition à blanc : chronométrer, identifier les points de friction
- Préparer le plan B si Colab plante (outputs JSON pré-sauvegardés à afficher)
- Désigner les rôles : qui pilote le code, qui présente les slides, qui répond aux questions
- Lancer la démo finale
- Débrief post-présentation équipe
