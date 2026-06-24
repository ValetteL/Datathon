# Rapport J1 — Comprendre la crise CNC × Ultia

> Datathon NEXA Digital School 2026 — Équipe : Alexis, Franck, Ruben, Malo, Baptiste, Louis  
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

## 3. Chiffres clés J1

| Indicateur | Valeur | Source |
|---|---|---|
| Volume total | 35 396 tweets | `load_corpus()` |
| Pic journalier | **7 303 tweets** le 27 mars 2026 | `notebooks/J1_exploration.ipynb` |
| Ratio RETWEET | *voir notebook* | `notebooks/J1_exploration.ipynb` |
| Comptes uniques | *voir notebook* | `notebooks/J1_exploration.ipynb` |
| Narratif dominant | *voir analyse Franck (P2)* | Exploration manuelle |

> Les valeurs calculées automatiquement sont dans `slides/chiffres_cles.json` (mis à jour par le notebook).

---

## 4. Grille des 5 axes d'analyse

### Axe 1 — Acteurs *(Ruben, P3)*

**Question** : Qui parle ? Qui amplifie ?

- Répartition par type : média / influenceur / institution / militant / anonyme
- Top 20 comptes par volume et par Shares reçus
- Identification des "tweets seeds" (ceux qui ont déclenché les vagues)
- Distribution comptes vérifiés vs non-vérifiés dans les phases de pic

*→ Résultats : à compléter en fin de J1*

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

*→ Exemples de tweets par narratif : à compléter par Franck pour calibrer l'AgentAnalyste*

---

### Axe 3 — Propagation *(Alexis, P1)*

**Question** : Comment et à quelle vitesse la crise s'est-elle répandue ?

- Courbe volume/heure sur toute la période
- Identification des 3-5 pics et leur déclencheur
- Durée de la crise, vitesse de montée, vitesse de descente
- Ratio RETWEET par heure (amplification vs opinion originale)

*→ Figure : `slides/figures/fig_timeline.png` (générée par notebook J1)*

---

### Axe 4 — Coordination *(Malo, P4)*

**Question** : La propagation est-elle spontanée ou orchestrée ?

- Rafales de tweets identiques en < 5 min (signe de copier-coller ou bot)
- Synchronie : tweets simultanés avec même hashtag / même mention
- Comptes récents (< 30 jours) dans les pics
- Clusters thématiques par horaire

*→ Résultats : à compléter en fin de J1*

---

### Axe 5 — Sémantique *(Franck, P2)*

**Question** : Comment le ton évolue-t-il au fil de la crise ?

- Top 30 termes/expressions par jour
- Glissements sémantiques entre J-début et J-fin de la crise
- Montée en agressivité (intensité du sentiment négatif)
- Vocabulaire dominant par camp

*→ Résultats : à compléter en fin de J1*

---

## 5. Architecture technique mise en place (J1)

Le pipeline LangGraph est entièrement structuré et partiellement implémenté :

```
load_corpus() → CrisisState → AgentAnalyste → AgentVeille → [HumanGate] → AgentStratège → AgentRédacteur → outputs/
```

| Composant | Fichier | Statut J1 |
|---|---|---|
| Chargeur corpus | `tools/corpus_loader.py` | ✅ Implémenté |
| État partagé | `pipeline/state.py` | ✅ Implémenté |
| Orchestrateur | `pipeline/graph.py` | ✅ Câblé |
| AgentVeille | `agents/veille.py` | ✅ Implémenté et testé |
| AgentAnalyste | `agents/analyste.py` | 🔧 Structure prête — Ruben finalise J2 |
| AgentStratège | `agents/stratege.py` | 🔧 Structure prête — Baptiste finalise J2 |
| AgentRédacteur | `agents/redacteur.py` | 🔧 Structure prête — Baptiste finalise J2 |
| HumanGate | `pipeline/graph.py` | ✅ Implémenté |
| Neutralité éditoriale | `prompts/prompts.py` | ✅ Centralisée (AD-4) |

### Décisions d'architecture contraignantes (AD)

Les AD-1 à AD-10 sont détaillées dans `_bmad-output/architecture/.../ARCHITECTURE-SPINE.md`. Les plus critiques pour J2 :

- **AD-1** : LangGraph StateGraph — pas de N8N, pas de LangChain seul
- **AD-2** : CrisisState TypedDict — seul vecteur de données entre agents
- **AD-3** : Gemini via `get_llm()` — modèle configurable par `GEMINI_MODEL` dans `.env`
- **AD-4** : `NEUTRALITY_SYSTEM_PROMPT` obligatoire sur chaque agent
- **AD-5** : `source_tweet_ids` obligatoire dans chaque output Pydantic (anti-hallucination)
- **AD-6** : Clé API jamais dans le code — `.env` ou Colab Secrets uniquement
- **AD-7** : HumanGate obligatoire avant toute génération de réponse

---

## 6. Généricité — réponse à la contrainte du jury

> *"Si demain c'est Coca-Cola, vos agents marchent ?"*

**Oui.** Le seul paramètre à changer est `corpus_config` :

```python
corpus_config = {
    "evenement": "Scandale Coca-Cola — boycott campagne pub",
    "periode":   "janvier-février 2027",
    "mots_cles": ["cocacola", "boycott", "publicité"],
}
```

Le pipeline charge n'importe quel corpus au format `data.xlsx`, les agents s'adaptent au contexte fourni, et les seuils de l'AgentVeille sont recalibrables par constantes.

---

## 7. Suivi du sprint

État J1 en fin de journée → `_bmad-output/implementation-artifacts/sprint-status.yaml`

**J2 — priorités immédiates :**
1. Ruben (P3) : finaliser `agents/analyste.py` avec few-shot examples de Franck
2. Baptiste (P5) : finaliser `agents/stratege.py` + `agents/redacteur.py`
3. Louis (P6) : intégration pipeline complet (`pipeline/graph.py` — Story 2.6)
4. Malo (P4) : valider `agents/veille.py` sur corpus réel, ajuster seuils si besoin
