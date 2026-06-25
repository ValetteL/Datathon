# 🧠 Crisis Intelligence — Multi-Agent AI System for Social Media Crisis Analysis

> **NEXA Digital School Datathon 2026** — Système multi-agents d'analyse et de gestion de crises virales sur X (Twitter)

---

## 📋 Description

**Crisis Intelligence** est un pipeline d'intelligence artificielle multi-agents conçu pour analyser en temps réel une crise virale sur les réseaux sociaux et générer automatiquement des recommandations de réponse institutionnelle.

Le système a été développé et calibré sur un cas réel : le **clash entre le streamer Ultia et le CNC (Centre National du Cinéma)** qui s'est déroulé sur X (Twitter) entre mars et mai 2026, générant **35 396 tweets** en langue française.

**Problème résolu :** Face à une crise virale, les institutions doivent analyser un volume massif de données en quelques heures, identifier les narratifs dominants, détecter les pics d'alertes, et rédiger une communication adaptée — sans disposition pour le faire manuellement à cette échelle.

---

## ✨ Fonctionnalités

- **Analyse de corpus** — Classification automatique des tweets par narratif et type d'acteur (via batch processing)
- **Veille de crise** — Détection des pics de volume et génération de signaux d'alerte horodatés
- **Validation humaine** — Checkpoint interactif (HumanGate) avant toute génération de réponse
- **Stratégie de réponse** — Proposition de 3 options institutionnelles calibrées (prudente / équilibrée / assertive)
- **Rédaction officielle** — Génération de communiqués dans 3 tonalités avec traçabilité des sources
- **Anti-hallucination** — Chaque sortie d'agent inclut des `source_tweet_ids` obligatoires pour ancrer les conclusions dans les données réelles
- **Interface terminal** — UI enrichie avec `rich` pour le suivi du pipeline en temps réel
- **Agnosticisme LLM** — Compatible Groq (llama-3.3-70b) et Google Gemini 2.0 Flash

---

## 🛠 Stack technique

### Langages
- **Python 3.11+**

### Frameworks & Orchestration
| Outil | Usage |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Orchestration StateGraph des agents |
| [LangChain](https://github.com/langchain-ai/langchain) | Binding LLM & chaînes de traitement |

### LLM Providers
| Provider | Modèle |
|---|---|
| [Groq](https://groq.com) | `llama-3.3-70b-versatile` |
| [Google Generative AI](https://ai.google.dev) | `gemini-2.0-flash` |

### Bibliothèques
| Bibliothèque | Rôle |
|---|---|
| `pydantic` v2 | Validation typée de toutes les sorties agents |
| `pandas` + `openpyxl` | Chargement et traitement du corpus Excel |
| `rich` | Interface terminal enrichie |
| `python-dotenv` | Gestion des variables d'environnement |
| `numpy` | Calculs numériques |

### Qualité & Outillage
| Outil | Rôle |
|---|---|
| `pyright` (basic mode) | Vérification statique des types |
| `python-dotenv` | Isolation des secrets |

---

## 🏛 Architecture

Le système adopte un pattern **pipes-and-filters** avec orchestration par **LangGraph StateGraph**. Un état partagé (`CrisisState`) circule séquentiellement entre les agents — aucun agent ne communique directement avec un autre.

```
Corpus Excel
    │
    ▼
CorpusLoader ──────────────────────────────────────────────────────┐
                                                                   │
                        CrisisState (TypedDict partagé)           │
                                                                   │
    ┌──────────────────────────────────────────────────────────────┘
    ▼
AgentAnalyste  ──►  AgentVeille  ──►  HumanGate  ──►  AgentStratège  ──►  AgentRédacteur
(Classification)  (Détection pics)  (Validation)   (3 options strat.)   (Communiqués)
                                        │
                               Feedback terminal
                               (interruption si rejet)
```

### Décisions architecturales non négociables (AD-1 à AD-10)

| # | Règle |
|---|---|
| AD-1 | LangGraph StateGraph uniquement — pas d'appels directs inter-agents |
| AD-2 | Un seul `CrisisState` TypedDict pour tout partage d'état |
| AD-3 | Chargement centralisé via `load_corpus()` — point d'entrée unique |
| AD-4 | Toutes les sorties agents sont des modèles Pydantic validés |
| AD-5 | Prompt de neutralité partagé entre tous les agents |
| AD-6 | HumanGate obligatoire avant génération de réponse |
| AD-7 | Fabrique LLM unique `get_llm()` — agnosticisme provider |
| AD-8 | Exécution strictement séquentielle |
| AD-9 | Configuration généralisée — aucun nom d'événement hardcodé |
| AD-10 | Anti-hallucination — `source_tweet_ids` obligatoires dans toutes les sorties |

---

## 📁 Structure du projet

```
Datathon/
├── src/
│   ├── agents/
│   │   ├── analyste.py          # Agent 1 — Classification narratifs (batch)
│   │   ├── veille.py            # Agent 2 — Détection pics & alertes
│   │   ├── stratege.py          # Agent 3 — 3 options stratégiques
│   │   └── redacteur.py         # Agent 4 — Rédaction communiqués
│   ├── pipeline/
│   │   ├── state.py             # CrisisState TypedDict (état partagé)
│   │   ├── schemas.py           # Modèles Pydantic (NarrativeResult, StrategyOptions…)
│   │   └── graph.py             # Assemblage StateGraph + HumanGate
│   ├── prompts/
│   │   └── prompts.py           # Fabrique LLM (get_llm()) + prompts neutralité
│   ├── tools/
│   │   └── corpus_loader.py     # Chargement, nettoyage, validation du corpus Excel
│   └── main.py                  # Point d'entrée — pipeline complet avec UI rich
│
├── Dataset/
│   ├── data.xlsx                # 35 396 tweets (corpus principal)
│   └── dictionnaire_bdd.xlsx    # Référentiel des colonnes
│
├── notebooks/
│   ├── analyse_J1.ipynb         # Exploration J1 — statistiques corpus
│   ├── analyse_J2.ipynb         # Développement J2
│   └── tuning_veille.ipynb      # Calibration agent Veille
│
├── docs/
│   ├── RAPPORT_J1.md            # Rapport d'analyse J1
│   └── planning.md
│
├── slides/
│   ├── presentation.html        # Slides de présentation
│   └── figures/                 # Graphiques générés
│       └── chiffres_cles.json   # Métriques clés du corpus
│
├── outputs/                     # Sorties JSON générées (gitignored)
│
├── _bmad-output/
│   └── architecture/            # Architecture BMAD (AD-1 à AD-10, invariants)
│
├── .env.example                 # Template des variables d'environnement
├── requirements.txt             # Dépendances Python
├── pyrightconfig.json           # Config Pyright (type checking)
├── GUIDE_BMAD.md               # Guide méthodologique BMAD
└── SPRINT.md                    # Plan de sprint 3 jours
```

---

## ⚙️ Installation

### Prérequis

- Python **3.11+**
- Clé API **Groq** et/ou **Google Generative AI**
- `pip` ou `pip3`

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd Datathon

# 2. Créer un environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Puis éditer .env avec vos clés API
```

---

## 🔧 Configuration

Copiez `.env.example` en `.env` et renseignez vos clés :

```env
# Provider LLM (choisir l'un ou l'autre)
GROQ_API_KEY=votre_cle_groq
GOOGLE_API_KEY=votre_cle_google

# Provider actif ("groq" ou "google")
LLM_PROVIDER=groq
```

Le choix du provider est centralisé dans `src/prompts/prompts.py` via la fabrique `get_llm()`.

---

## 🚀 Lancement

```bash
# Lancer le pipeline complet
python src/main.py
```

Le pipeline s'exécute séquentiellement :

1. **Chargement** du corpus (35 396 tweets depuis `Dataset/data.xlsx`)
2. **AgentAnalyste** — classification par narratif et type d'acteur (batch processing)
3. **AgentVeille** — détection des pics de volume, génération des signaux d'alerte
4. **HumanGate** — validation interactive dans le terminal avant de continuer
5. **AgentStratège** — proposition de 3 options de réponse institutionnelle
6. **AgentRédacteur** — génération des communiqués officiels
7. **Sauvegarde** des sorties JSON dans `outputs/`

> Le HumanGate interrompt le pipeline et attend une décision explicite de l'opérateur avant de générer toute communication officielle.

---

## 📊 Données du corpus

| Métrique | Valeur |
|---|---|
| Volume total | 35 396 tweets |
| Période | 19 mars – 1er mai 2026 |
| Langue | 100% français |
| Pic journalier | 7 303 tweets (27 mars 2026) |
| Distribution | 85,8% retweets · 10,2% replies · 2,1% quotes |
| Sentiment négatif | 30,68% |
| Sentiment neutre | 66,3% |
| Comptes uniques | 10 437 |
| Comptes vérifiés | 9,14% |

---

## 🤖 Utilisation / Pipeline

Le pipeline expose ses résultats via l'état `CrisisState` et des sorties JSON structurées.

### Sorties Pydantic attendues par agent

```python
# AgentAnalyste → NarrativeResult
{
  "narrative_type": str,          # ex: "soutien_createur", "critique_cnc"
  "actor_type": str,              # ex: "fan", "journaliste", "institution"
  "confidence": float,
  "source_tweet_ids": list[str]   # obligatoire (anti-hallucination)
}

# AgentVeille → AlertSignal
{
  "peak_date": str,
  "peak_volume": int,
  "alert_level": Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"],
  "key_narratives": list[str],
  "source_tweet_ids": list[str]
}

# AgentStratège → StrategyOptions
{
  "option_prudente": {...},
  "option_equilibree": {...},
  "option_assertive": {...}
}

# AgentRédacteur → DraftCommunique
{
  "tonalite_choisie": str,
  "communique": str,
  "source_tweet_ids": list[str]
}
```

### Exécution dans Google Colab

```python
# Installation des dépendances
!pip install -r requirements.txt

# Configuration
import os
os.environ["GROQ_API_KEY"] = "votre_cle"
os.environ["LLM_PROVIDER"] = "groq"

# Lancement
!python src/main.py
```

---

## 🧪 Tests

> Aucune suite de tests automatisés n'est présente dans le projet actuellement.

La vérification statique des types est configurée via **Pyright** :

```bash
# Vérification de types (mode basic)
pyright src/
```

---

## 🔒 Sécurité

- Les clés API sont isolées dans `.env` (exclu du contrôle de version via `.gitignore`)
- Un fichier `.env.example` documente les variables sans exposer les valeurs
- Aucun secret n'est hardcodé dans le code source
- Les sorties agents incluent des `source_tweet_ids` pour assurer la traçabilité et limiter les hallucinations

---

## 🚢 Déploiement

Le projet est conçu pour être exécuté dans **Google Colab** (environnement partagé de l'équipe lors du Datathon).

```bash
# Cloner depuis Colab
!git clone <url-du-repo>
%cd Datathon
!pip install -r requirements.txt

# Configurer les secrets Colab
from google.colab import userdata
os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
```

> Pas de CI/CD configuré pour ce projet — déploiement manuel adapté au format Datathon.

---

## 💡 Améliorations possibles

| Priorité | Suggestion |
|---|---|
| ⭐⭐⭐ | Ajouter une suite de tests (pytest) pour chaque agent avec des fixtures de tweets |
| ⭐⭐⭐ | Implémenter un mode parallèle pour le batch de l'AgentAnalyste (async LangGraph) |
| ⭐⭐ | Exporter les résultats vers un dashboard Streamlit ou Gradio |
| ⭐⭐ | Ajouter un cache LangSmith pour réduire les coûts API en re-runs |
| ⭐⭐ | Configurer LangSmith tracing pour l'observabilité du pipeline |
| ⭐ | Dockeriser l'environnement pour reproductibilité hors Colab |
| ⭐ | Étendre le corpus loader à d'autres sources (CSV, API X/Twitter) |
| ⭐ | Ajouter des métriques de confiance agrégées au niveau pipeline |

---

## 👥 Auteur & Équipe

Projet réalisé dans le cadre du **NEXA Digital School Datathon 2026**.

| Rôle | Personne |
|---|---|
| Product Manager / Arch. | Louis |
| Développeur P1 | Alexis |
| Développeur P2 | Franck |
| Développeur P3 | Ruben |
| Développeur P4 | Malo |
| Développeur P5 | Baptiste |

---

## 📄 Licence

Ce projet a été développé dans un cadre académique et compétitif. Tous droits réservés à l'équipe.

---

*Généré avec [Claude Code](https://claude.ai/code) — NEXA Datathon 2026*
