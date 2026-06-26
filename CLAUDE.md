# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent LangGraph pipeline for analyzing the viral social media crisis "Affaire Ultia × CNC" (mars-avril 2026, ~35k tweets). The pipeline classifies narratives, detects alert signals, and generates institutional response drafts — with a mandatory human validation gate before generating responses.

**Team**: Alexis (P1 — temporalité), Franck (P2 — narratifs/sémantique), Ruben (P3 — acteurs/analyste), Malo (P4 — coordination/veille), Baptiste (P5 — orchestration/stratège/rédacteur), Louis (chef de projet / intégration).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your API key
```

`.env` required variables:
- `IA_PROVIDER` — `GROQ` (default) or `GEMINI`
- `GROQ_API_KEY` — if using Groq (console.groq.com)
- `GOOGLE_API_KEY` — if using Gemini (aistudio.google.com)
- `GROQ_MODEL` — optional, defaults to `llama-3.3-70b-versatile`
- `GEMINI_MODEL` — optional, defaults to `gemini-2.0-flash`

On Google Colab, set the relevant key(s) in Colab Secrets and call `load_dotenv()` (or `os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")`).

Validate setup:
```python
from tools.corpus_loader import load_corpus
from prompts.prompts import get_llm

df = load_corpus("Dataset/data.xlsx")  # should print: 35,396 tweets
llm = get_llm()
print(llm.invoke("Réponds juste OK.").content)
```

## Running the pipeline

**Interactive demo (Veille → HumanGate → Stratège → Rédacteur):**
```bash
python src/main.py
```
This uses a mocked `narratives` state (AgentAnalyste not yet wired) and displays results with `rich` formatted panels. Run from the project root.

**Full LangGraph pipeline (once AgentAnalyste is implemented):**
```bash
python pipeline/graph.py
```

## Directory structure

```
Datathon/
├── agents/                  # Root-level agents (canonical location)
│   └── veille.py            # AgentVeille — implemented ✅
├── src/                     # Baptiste's J2 implementations
│   ├── agents/
│   │   ├── stratege.py      # AgentStratège — implemented ✅
│   │   └── redacteur.py     # AgentRédacteur — implemented ✅
│   ├── pipeline/
│   │   └── graph.py         # Updated graph with conditional imports
│   └── main.py              # Interactive demo runner (rich UI)
├── pipeline/
│   ├── state.py             # CrisisState TypedDict
│   └── graph.py             # LangGraph orchestrator
├── prompts/
│   └── prompts.py           # get_llm() factory + get_system_prompt()
├── tools/
│   └── corpus_loader.py     # load_corpus() — sole entry point for data.xlsx
├── notebooks/
│   └── J1_exploration.ipynb # J1 EDA — Louis (metrics, timeline, sentiment)
├── slides/
│   ├── chiffres_cles.json   # Key J1 metrics (partially filled — team updates)
│   └── figures/             # fig_timeline.png, fig_sentiment.png
├── docs/
│   ├── RAPPORT_J1.md        # J1 analysis report
│   └── planning.md
├── Dataset/                 # gitignored — share via Teams
│   └── data.xlsx
└── outputs/                 # gitignored — generated at runtime
```

> `src/main.py` runs with `src/` prepended to `sys.path` (script directory rule). `src/agents/` overrides root `agents/` for modules that exist in both; modules absent from `src/agents/` (e.g. `veille.py`) resolve to root. No `PYTHONPATH` needed when running from the project root.

**Type checking:** `pyrightconfig.json` targets `src/` with `.venv` and Python 3.14.

## Architecture

### Pipeline flow (LangGraph StateGraph)

```
Dataset/data.xlsx
    → load_corpus()          # tools/corpus_loader.py — only entry point for raw data
    → CrisisState            # pipeline/state.py — shared TypedDict, sole inter-node bus
    → AgentAnalyste          # agents/analyste.py   [TODO — Ruben P3] → NarrativeResult
    → AgentVeille            # agents/veille.py      [DONE ✅]        → AlertSignal
    → HumanGate (interrupt)  # pipeline/graph.py — mandatory pause, human types yes/no
    → AgentStratège          # src/agents/stratege.py [DONE ✅]       → StrategyOptions
    → AgentRédacteur         # src/agents/redacteur.py [DONE ✅]      → DraftCommunique
    → save_outputs()         # outputs/<key>_<run_id>.json
```

`src/pipeline/graph.py` uses conditional imports — the graph starts even if `agents/analyste.py` doesn't exist yet; it raises `NotImplementedError` only when that node is reached.

### Key files

| File | Role |
|---|---|
| `pipeline/state.py` | `CrisisState` TypedDict — the only data contract between all nodes |
| `pipeline/graph.py` | `build_graph()`, `init_state()`, `human_gate()`, `save_outputs()` |
| `tools/corpus_loader.py` | `load_corpus()` — handles all type casting and cleaning of `data.xlsx` |
| `prompts/prompts.py` | `get_llm()` factory (GROQ/GEMINI) + `get_system_prompt(agent_name)` |
| `agents/veille.py` | Fully implemented reference agent — study before writing new agents |
| `src/agents/stratege.py` | AgentStratège implementation |
| `src/agents/redacteur.py` | AgentRédacteur implementation |
| `src/main.py` | Interactive demo — runs pipeline with mocked Analyste and rich terminal UI |

### LLM pattern used by every agent

```python
parser = PydanticOutputParser(pydantic_object=MyOutputModel)
llm = get_llm()  # never instantiate ChatGroq / ChatGoogleGenerativeAI directly
prompt = ChatPromptTemplate.from_messages([
    ("system", get_system_prompt("agent_name")),
    ("human", "... {format_instructions}"),
])
result: MyOutputModel = (prompt | llm | parser).invoke({..., "format_instructions": parser.get_format_instructions()})
state["my_field"] = result.model_dump()
```

After LLM parsing, always **override metric fields with pandas-computed values** (the LLM only writes the `summary` text). See `agents/veille.py:140-147` for the pattern.

## Architectural decisions (non-negotiable)

| Rule | What it forbids |
|---|---|
| **AD-1** LangGraph StateGraph is the only orchestrator | Direct agent-to-agent calls outside the graph |
| **AD-2** `CrisisState` is the only inter-node data bus | Global variables, side effects, returning new state objects |
| **AD-3** `load_corpus()` is the only way to read `data.xlsx` | Any agent or notebook reading the Excel directly |
| **AD-4** Every agent output is a typed Pydantic model | Free-text or unvalidated dict outputs |
| **AD-5** All prompts come from `prompts/prompts.py` | System prompts hardcoded inside agent files |
| **AD-6** HumanGate is mandatory before AgentStratège | `human_approved=True` without the interrupt |
| **AD-7** `get_llm()` factory for all LLM instantiation | API key hardcoded in code, different providers per agent |
| **AD-8** Strict sequence: Analyste → Veille → HumanGate → Stratège → Rédacteur | Parallelism or reordering |
| **AD-9** `corpus_config` dict injected at `init_state()` | Hardcoding "Ultia", "CNC", or "mars 2026" inside agent files |
| **AD-10** `source_tweet_ids` required in every Pydantic output | Claims without traceable `postID` sources |

## Corpus notes

- 35,396 tweets, 100% French, 19 mars → 1er mai 2026, ~95 MB in RAM
- Each row = one act of diffusion (retweet, reply, quote, or original post)
- **Confirmed J1 metrics**: peak 7,303 tweets on 2026-03-27, 85.8% retweets, 10,437 unique accounts, 30.7% negative sentiment, 9.1% verified accounts
- **Reliable signal**: tweet volume per hour/day (`Date` column), `Engagement Type`, `Sentiment`
- **Sparse but meaningful**: `Likes`/`Shares`/`Comments` > 0 are real viral signals (93-98% are zero due to collection artefact)
- **Ignore**: `Impressions` (6.7% non-null), `Reach` (correlated + 20k duplicates), `Hashtags` (95.7% empty)
- Alert thresholds in `agents/veille.py`: >2,000 tweets/day, >90% RT ratio, >50 likes, >20 shares

## Remaining agent to implement

### `agents/analyste.py` — Ruben (P3), J2

Output: `NarrativeResult` with `analyses: list[TweetAnalysis]`, `narratif_dominant`, `repartition` (counts per narrative), `source_tweet_ids`.

Narratif categories: `censure | copinage | defense_ultia | defense_cnc | autre`
Acteur categories: `media | militant | influenceur | anonyme | institution`

Use `state["tweets_sample"]` (500-tweet subset). Process in batches of ~200 tweets formatted as `[postID] @Author (followers:N, verified:B, type:T)\nmessage_normalizer`.

## J1 outputs

Key metrics are in `slides/chiffres_cles.json`. Fields still pending from team members: `narratif_dominant` (Franck), `top_acteur_type` (Ruben), `note_coordination` (Malo), `terme_dominant` (Franck). Figures generated in `slides/figures/`. Full analysis in `docs/RAPPORT_J1.md`.

## Sprint tracking

Update `_bmad-output/implementation-artifacts/sprint-status.yaml` when starting or completing stories. Statuses: `backlog → in-progress → review → done`. Full story specs in `_bmad-output/planning-artifacts/epics.md`.
