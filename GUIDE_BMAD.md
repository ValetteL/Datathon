# Guide BMAD — Datathon CNC × Ultia

> Ce guide explique comment la méthode BMAD a été utilisée pour cadrer ce projet, et comment tu peux toi-même invoquer ces outils pour continuer le travail.

---

## Qu'est-ce que BMAD ?

**BMAD (Breakthrough Method for Agile Development)** est un système de *skills* pour Claude Code qui transforme l'IA en coach structuré pour les phases de projet : brainstorming, architecture, spécification, stories, etc.

Plutôt que de simplement "demander à l'IA de faire quelque chose", BMAD impose un protocole rigoureux :
- Il garde une **mémoire de session** dans `.memlog.md` (append-only — rien n'est jamais effacé)
- Il produit des **artefacts versionnés** dans `_bmad-output/`
- Il suit des règles éditoriales et des templates précis

---

## Installation de BMAD (à faire une fois par poste)

### Prérequis

- **Node.js ≥ 18** installé ([nodejs.org](https://nodejs.org)) — pour `npx`
- **Claude Code** (CLI ou extension VS Code) — ou Cursor / Windsurf selon ton IDE

### Commande d'installation

Dans le dossier racine du projet cloné :

```bash
npx bmad-method install
```

L'installateur est interactif. Il te demande :

1. **Quel agent / IDE tu utilises** — choisis selon ton setup :

   | IDE / Agent | Choisir dans l'installateur | Skills installés dans |
   |---|---|---|
   | **Claude Code** (CLI ou VS Code) | `Claude Code` | `.claude/skills/` |
   | **Cursor** | `Cursor` | `.cursor/rules/` |
   | **Windsurf** | `Windsurf` | `.windsurf/rules/` |
   | **Autre / générique** | `Generic Agent` | `.agent/skills/` |

2. **Langue de communication** — tape `French` pour travailler en français avec l'agent

3. **Nom du projet** — tape `Datathon CNC Ultia`

L'installateur écrit ensuite `_bmad/` (scripts internes) et le dossier de skills adapté à ton IDE. Ces dossiers sont **gitignorés** — chaque membre les regénère sur son poste.

### Vérifier que l'installation a fonctionné

**Sur Claude Code :** ouvre le projet dans le terminal ou VS Code, lance `claude`, puis tape `/bmad-brainstorming` — tu dois voir le skill s'activer.

**Sur Cursor / Windsurf :** ouvre le projet, les skills apparaissent dans les règles de l'agent (les `@` rules). Tape `/bmad-` dans le chat pour voir les complétions.

### Config du projet (déjà faite, ne pas retoucher)

Le fichier `_bmad/core/config.yaml` (regénéré à l'install) est déjà configuré pour ce projet avec la version **6.9.0**. Si tu veux changer la langue ou le nom du projet après install, édite directement :

```yaml
# _bmad/core/config.yaml
user_name: Ton Prénom
communication_language: French
document_output_language: French
```

---

## Ce qui a déjà été fait avec BMAD

### 1. Brainstorming — 115 idées générées

```
_bmad-output/brainstorming/brainstorm-crise-reseaux-sociaux-agents-ia-2026-06-24/
├── .memlog.md          ← journal complet de la session
└── brainstorm.html     ← rendu visuel des idées (ouvrir dans un navigateur)
```

La session a couvert : First Principles, Mind Mapping, Jobs-to-be-Done, Six Chapeaux, What If Scenarios. Toutes les pistes explorées y sont, y compris les idées abandonnées.

### 2. Architecture — Décisions structurantes AD-1 à AD-10

```
_bmad-output/architecture/architecture-datathon-cnc-ultia-2026-06-24/
├── .memlog.md              ← journal de toutes les décisions d'architecture
├── ARCHITECTURE-SPINE.md   ← spine technique (contrat de convergence)
└── PROJET-ARCHITECTURE.md  ← document à lire en premier ← TOI ET TOUTE L'ÉQUIPE
```

**Commence par lire `_bmad-output/architecture/.../PROJET-ARCHITECTURE.md`** — c'est le contrat technique que tout le monde doit connaître avant de coder.

---

## Comment utiliser BMAD dans Claude Code

### Prérequis

1. Avoir **Claude Code** installé (CLI ou extension VS Code)
2. Être dans le dossier racine du projet : `cd /chemin/vers/Datathon`
3. Lancer Claude Code : `claude` dans le terminal

### Invoquer un skill

Dans la conversation avec Claude Code, tape `/` suivi du nom du skill :

| Commande | Usage |
|---|---|
| `/bmad-brainstorming` | Lancer ou reprendre une session de brainstorming |
| `/bmad-create-architecture` | Créer ou mettre à jour l'architecture |
| `/bmad-spec` | Écrire une spec fonctionnelle structurée |
| `/bmad-create-story` | Décomposer une epic en stories actionnables |

### Reprendre une session existante

BMAD détecte automatiquement les sessions précédentes et propose de les reprendre. Si tu veux continuer le brainstorming ou affiner l'architecture, invoque le skill — il lira le `.memlog.md` existant et repartira de là.

---

## Règles du jeu BMAD sur ce projet

### 1. Le memlog est sacré

Le fichier `.memlog.md` dans chaque dossier `_bmad-output/` est **append-only** : on n'y efface rien, on n'y réécrit rien. Si une décision change, on ajoute une entrée qui superpose. C'est un journal de bord.

### 2. Les AD sont des contrats

Les décisions d'architecture (AD-1 à AD-10) dans `ARCHITECTURE-SPINE.md` sont **contraignantes pour tout le monde**. Si tu penses qu'une AD doit changer, on en discute en équipe — on ne la contourne pas silencieusement.

Les plus critiques :

| AD | Règle |
|---|---|
| AD-1 | Framework : **LangGraph StateGraph** — pas N8N, pas LangChain seul |
| AD-2 | État partagé : **CrisisState TypedDict** — aucun agent ne passe de données autrement |
| AD-3 | LLM : **Gemini 2.0 Flash** via `get_llm()` dans `prompts/prompts.py` — un seul point d'entrée |
| AD-4 | Neutralité : **NEUTRALITY_SYSTEM_PROMPT** obligatoire sur chaque agent |
| AD-5 | Anti-hallucination : **`source_tweet_ids` obligatoire** dans chaque output Pydantic |
| AD-6 | Clé API : **jamais dans le code** — uniquement `os.environ` ou Colab Secrets |
| AD-7 | Validation humaine : **HumanGate obligatoire** avant tout output de communication |

### 3. Chaque agent est isolé

Un agent lit depuis `state[...]` et écrit dans `state[...]`. Jamais d'appels directs entre agents. C'est LangGraph qui orchestre.

---

## Structure du projet

```
Datathon/
├── agents/
│   ├── veille.py          ← AgentVeille (FAIT — détection d'alerte via volume + viraux)
│   ├── analyste.py        ← AgentAnalyste (À FAIRE — P3, J2)
│   ├── stratege.py        ← AgentStratège (À FAIRE — P5, J2)
│   └── redacteur.py       ← AgentRédacteur (À FAIRE — P5, J2-J3)
├── pipeline/
│   ├── state.py           ← CrisisState TypedDict (schéma partagé)
│   └── graph.py           ← Assemblage du StateGraph + HumanGate
├── tools/
│   └── corpus_loader.py   ← Seule fonction autorisée à lire Dataset/
├── prompts/
│   └── prompts.py         ← Neutralité centralisée + factory get_llm()
├── notebooks/             ← Jupyter notebooks (exploration J1)
├── outputs/               ← Outputs JSON des runs (gitignorés)
├── docs/                  ← Documents équipe (planning, rapport cadrage)
├── Dataset/               ← Données (gitignorées — partager via Drive)
│   ├── data.xlsx          ← 35 396 tweets (19 mars → 1er mai 2026)
│   └── dictionnaire_bdd.xlsx
├── _bmad-output/          ← Artefacts BMAD (brainstorming + architecture)
├── requirements.txt
├── .gitignore
└── GUIDE_BMAD.md          ← ce fichier
```

---

## Setup en 3 minutes

```bash
# 1. Cloner le repo
git clone <url-du-repo>
cd Datathon

# 2. Créer l'environnement
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
# ou : .venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API Gemini
# Option A — fichier .env (ne jamais committer)
echo "GOOGLE_API_KEY=ta_cle_ici" > .env

# Option B — variable d'environnement (recommandé)
export GOOGLE_API_KEY="ta_cle_ici"

# Sur Google Colab (recommandé) :
# Secrets > ajouter GOOGLE_API_KEY > puis dans le notebook :
# from google.colab import userdata
# import os
# os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')

# 5. Obtenir les données
# Télécharger Dataset/ depuis Teams
# Placer data.xlsx et dictionnaire_bdd.xlsx dans Dataset/

# 6. Vérifier que tout fonctionne
python -c "from tools.corpus_loader import load_corpus; df = load_corpus(); print(len(df), 'tweets chargés')"
```

---

## Qualité des données — à lire avant de coder

Le corpus a des particularités importantes documentées dans `tools/corpus_loader.py` :

| Signal | Fiabilité | Usage recommandé |
|---|---|---|
| Volume (tweets/heure) | 100% | **Signal principal** — chaque ligne = un acte de diffusion |
| Engagement Type (RETWEET/REPLY/QUOTE) | 98% | Vitesse d'amplification |
| Sentiment (pré-calculé NLP) | 100% | Évolution du ton |
| Full Text / message_normalizer | 100% | Input LLM |
| Likes / Shares (non-nuls) | 100%* | Signal viral rare (* seulement 2-7% ont une valeur) |
| Impressions | Ignorer | 6.7% non-nuls, incohérent |
| Reach | Ignorer | Corrélé à Impressions + 20k doublons |
| Hashtags | Limité | 95.7% vides |

---

## Questions ?

- Architecture : voir `_bmad-output/architecture/.../PROJET-ARCHITECTURE.md`
- Décisions techniques : voir `_bmad-output/architecture/.../ARCHITECTURE-SPINE.md`
- Toutes les idées explorées : voir `_bmad-output/brainstorming/.../brainstorm.html`
