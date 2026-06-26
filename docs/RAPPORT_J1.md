# Rapport J1 — Comprendre la crise CNC × Ultia

> Datathon NEXA Digital School 2026 — Équipe : Alexis · Franck · Ruben · Malo · Baptiste · Louis  
> Journée 1 — Exploration du corpus et mise en place du pipeline

---

## 1. Contexte et mission

Le datathon porte sur la crise virale déclenchée entre mars et mai 2026 opposant la plateforme de streaming **Ultia** au **CNC** (Centre National du Cinéma et de l'Image Animée).

**Les faits** (niveau 1 — non interprétés) :
- Ultia déclare en live Twitch vouloir favoriser ses proches et écarter les projets d'extrême droite dans le cadre de son rôle de jurée CNC
- Le CNC publie un tweet la destituant immédiatement
- Cascade de tweets en réaction : médias, internautes, militants, créateurs
- Sous la pression et des menaces signalées, la commission d'aide est suspendue (programme ~3M€)

**Notre mission** : construire un outil multi-agents capable de comprendre ce type de crise, de détecter ses signaux d'amplification, et d'aider une institution à formuler une réponse — le tout réutilisable sur n'importe quel cas similaire.

---

## 2. Le corpus

| Propriété | Valeur |
|---|---|
| Fichier source | `Dataset/data.xlsx` |
| Volume | **35 396 tweets** |
| Période | 19 mars 2026 → 1er mai 2026 |
| Langue | 100% français |
| Chargement | `tools/corpus_loader.py → load_corpus()` |

### Qualité des données — points d'attention

| Colonne | Fiabilité | Note |
|---|---|---|
| `Date`, `postID`, `Author` | ✅ 100% | Colonnes structurelles fiables |
| `Engagement Type` | ✅ ~98% | Signal principal de propagation |
| `Sentiment` | ✅ 100% | Pré-calculé NLP, utilisable tel quel |
| `Full Text` / `message_normalizer` | ✅ 100% | Préférer `message_normalizer` pour le LLM |
| `Likes` / `Shares` | ⚠️ 2-7% non-nuls | Rare mais fort : ces tweets sont les vrais viraux |
| `Impressions` | ❌ 6.7% non-nuls | Incohérent — ignorer |
| `Reach` | ❌ 39.9% non-nuls | Corrélé à Impressions + ~20k doublons — ignorer |
| `Hashtags` | ⚠️ 4.3% non-vides | Usage limité en analyse |
| `City` / `City Code` | ⚠️ ~50% vides | Analyse géographique limitée |

**Règle fondamentale** : dans ce corpus de crise, chaque ligne = **un acte de diffusion**. Le signal de crise est le **volume** (tweets/heure), pas l'engagement individuel.

---

## 3. Chiffres clés

Les valeurs calculées sont centralisées dans `slides/chiffres_cles.json` — chaque responsable renseigne sa section dans ce fichier.  
Chiffres Louis calculés et JSON mis à jour (`notebooks/J1_exploration.ipynb`). Figures générées dans `slides/figures/`.

Distribution engagement : RETWEET 85,8% · REPLY 10,2% · QUOTE 2,1% · ORIGINAL 1,9%  
Distribution sentiment : neutral 66,3% · **negative 30,7%** · positive 3,0%

| Indicateur | Valeur | Responsable |
|---|---|---|
| Volume total | **35 396 tweets** | ✅ Louis (notebook) |
| Pic journalier | **7 303 tweets** le 27 mars 2026 | ✅ Louis (notebook) |
| Ratio RETWEET | **85,8%** | ✅ Louis (notebook) |
| Comptes uniques | **10 437** | ✅ Louis (notebook) |
| Taux de négativité | **30,7%** | ✅ Louis (notebook) |
| Narratif dominant | *→ analyse Franck (J2)* | Franck — clé `narratif_dominant` |
| Type d'acteur majoritaire | *→ analyse Ruben (J2)* | Ruben — clé `top_acteur_type` |
| Terme dominant | *→ analyse Franck (J2)* | Franck — clé `terme_dominant` |
| Note coordination | *→ analyse Malo (J2)* | Malo — clé `note_coordination` |

---

## 4. Grille des 5 axes d'analyse

### Axe 1 — Acteurs *(Ruben, P3)*

**Question** : Qui parle ? Qui amplifie ?

- Répartition par type : média / influenceur / institution / militant / anonyme
- Top 20 comptes par volume et par Shares reçus
- Identification des "tweets seeds" (ceux qui ont déclenché les vagues)
- Distribution comptes vérifiés vs non-vérifiés dans les phases de pic

**→ Ruben** : renseigner `top_acteur_type` dans `slides/chiffres_cles.json`

---

### Axe 2 — Narratifs *(Franck, P2)*

**Question** : De quoi parle-t-on vraiment ?

Narratifs pressentis à partir de la lecture du corpus :

| Narratif | Description |
|---|---|
| `censure` | Ultia victime d'une censure idéologique de l'institution |
| `copinage` | Ultia accusée de favoritisme envers ses proches |
| `defense_ultia` | Soutien à Ultia, dénonciation de la réaction du CNC |
| `defense_cnc` | Soutien à la décision du CNC, respect des règles |
| `autre` | Hors-sujet, ironique, non classifiable |

**→ Franck** : identifier le narratif dominant, renseigner `narratif_dominant` dans `slides/chiffres_cles.json`.  
Préparer 2-3 exemples de tweets par narratif — ils serviront à calibrer l'AgentAnalyste en J2.

---

### Axe 3 — Propagation *(Alexis, P1)*

**Question** : Comment et à quelle vitesse la crise s'est-elle répandue ?

- Courbe volume/heure sur toute la période
- Identification des 3-5 pics et leur déclencheur
- Durée de la crise, vitesse de montée, vitesse de descente
- Ratio RETWEET par heure (amplification vs opinion originale)

**→ Figure** : `slides/figures/fig_timeline.png` — générée par `notebooks/J1_exploration.ipynb`

---

### Axe 4 — Coordination *(Malo, P4)*

**Question** : La propagation est-elle spontanée ou orchestrée ?

- Rafales de tweets identiques en < 5 min (signe de copier-coller ou bot)
- Synchronie : tweets simultanés avec même hashtag / même mention
- Comptes récents (< 30 jours) dans les pics
- Clusters thématiques par horaire

**→ Malo** : renseigner `note_coordination` dans `slides/chiffres_cles.json`

---

### Axe 5 — Sémantique *(Franck, P2)*

**Question** : Comment le ton évolue-t-il au fil de la crise ?

- Top 30 termes/expressions par jour
- Glissements sémantiques entre J-début et J-fin de la crise
- Montée en agressivité (intensité du sentiment négatif)
- Vocabulaire dominant par camp

**→ Franck** : renseigner `terme_dominant` dans `slides/chiffres_cles.json`

---

## 5. Architecture technique

Pipeline complet implémenté. Tous les agents sont opérationnels et exposés via une API FastAPI. Une interface React permet de piloter le pipeline et de consulter les sessions passées.

```
load_corpus() → CrisisState → AgentAnalyste → AgentVeille → [HumanGate] → AgentStratège → AgentRédacteur → outputs/
```

| Composant | Fichier | Statut |
|---|---|---|
| Chargeur corpus | `backend/src/tools/corpus_loader.py` | ✅ Implémenté |
| État partagé | `backend/src/pipeline/state.py` | ✅ Implémenté |
| Persistance sessions | `backend/src/pipeline/session_store.py` | ✅ JSON sur disque (`outputs/`) |
| AgentAnalyste | `backend/src/agents/analyste.py` | ✅ Implémenté — **Ruben (P3)** |
| AgentVeille | `backend/src/agents/veille.py` | ✅ Implémenté et testé |
| AgentStratège | `backend/src/agents/stratege.py` | ✅ Implémenté — **Baptiste (P5)** |
| AgentRédacteur | `backend/src/agents/redacteur.py` | ✅ Implémenté — **Baptiste (P5)** |
| API FastAPI | `backend/main.py` | ✅ 7 endpoints |
| HumanGate | Interface React + `POST /analyse/rejeter` | ✅ Implémenté |
| Interface React | `frontend/src/` | ✅ Pipeline complet avec sessions |

**Lancement** : voir `backend/README.md` et `frontend/README.md`.

### Contraintes d'architecture

| Contrainte | Règle |
|---|---|
| Orchestration | LangGraph StateGraph uniquement — pas d'appels directs entre agents |
| Données partagées | `CrisisState` TypedDict — seul vecteur entre les agents |
| LLM | Utiliser `get_llm()` depuis `prompts/prompts.py` — jamais de clé en dur dans le code |
| Neutralité | `NEUTRALITY_SYSTEM_PROMPT` obligatoire dans chaque agent |
| Anti-hallucination | `source_tweet_ids` obligatoire dans chaque output Pydantic |
| Validation humaine | HumanGate obligatoire avant AgentStratège — ne pas contourner |

---

## 6. Setup

```bash
# 1. Cloner le repo
git clone https://github.com/ValetteL/Datathon.git && cd Datathon

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API Gemini
cp .env.example .env
# Éditer .env → GOOGLE_API_KEY=ta_clé_ici

# 4. Déposer le dataset (partagé via Teams — ne pas committer)
# Dataset/data.xlsx

# 5. Vérifier que l'environnement est OK
python -c "from agents.veille import run_veille; print('OK')"
```

**Clé API** : obtenir sur `https://aistudio.google.com` → "Get API key". Gratuit, quota individuel.  
**Dataset** : partagé via Teams uniquement. Ne jamais committer `Dataset/` (gitignore en place).

---

## 7. Généricité — réponse à la contrainte du jury

> *"Si demain c'est Coca-Cola, vos agents marchent ?"*

**Oui.** Le seul paramètre à changer est `corpus_config` dans `pipeline/graph.py` :

```python
corpus_config = {
    "evenement": "Scandale Coca-Cola — boycott campagne pub",
    "periode":   "janvier-février 2027",
    "mots_cles": ["cocacola", "boycott", "publicité"],
}
```

Le pipeline charge n'importe quel corpus au format `data.xlsx`, les agents s'adaptent au contexte fourni, et les seuils de l'AgentVeille sont recalibrables par constantes dans `agents/veille.py`.

---

## 8. Priorités J2

| Qui | Quoi | Statut |
|---|---|---|
| **Baptiste (P5)** | Implémenter `agents/stratege.py` + `agents/redacteur.py` | ✅ Fait (`src/agents/`) |
| **Ruben (P3)** | Implémenter `agents/analyste.py` | ⬜ Dernier bloc manquant |
| **Louis** | Intégration pipeline complet | ⏳ En attente AgentAnalyste |
| **Malo (P4)** | Valider `agents/veille.py` sur corpus réel, ajuster seuils | ⬜ `note_coordination` dans JSON |
| **Franck (P2)** | Finaliser analyse narratifs + few-shot examples | ⬜ `narratif_dominant` + `terme_dominant` dans JSON |
| **Alexis (P1)** | Tests pipeline J2 | ⬜ À faire dès que AgentAnalyste est pushé |

> **Demo intermédiaire disponible** : `python src/main.py` tourne avec un `narratives` mocké.
> Permet de tester Veille → Stratège → Rédacteur sans attendre l'AgentAnalyste.

Suivi sprint → `_bmad-output/implementation-artifacts/sprint-status.yaml`
