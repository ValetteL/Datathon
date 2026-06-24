from __future__ import annotations
import json
import os
import uuid
import pandas as pd
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from pipeline.state import CrisisState
from tools.corpus_loader import load_corpus
from agents.veille import run_veille


# ── Nœuds placeholder (à remplacer par les vrais agents J2) ──────────────────

def run_analyste(state: CrisisState) -> CrisisState:
    """Nœud AgentAnalyste — à implémenter dans agents/analyste.py (P3, J2)."""
    raise NotImplementedError("Implémente agents/analyste.py — voir PROJET-ARCHITECTURE.md §5.2")


def run_stratege(state: CrisisState) -> CrisisState:
    """Nœud AgentStratège — à implémenter dans agents/stratege.py (P5, J2)."""
    assert state["human_approved"], "HumanGate non validé."
    raise NotImplementedError("Implémente agents/stratege.py — voir PROJET-ARCHITECTURE.md §5.5")


def run_redacteur(state: CrisisState) -> CrisisState:
    """Nœud AgentRédacteur — à implémenter dans agents/redacteur.py (P5, J2-J3)."""
    raise NotImplementedError("Implémente agents/redacteur.py — voir PROJET-ARCHITECTURE.md §5.6")


# ── HumanGate ─────────────────────────────────────────────────────────────────

def human_gate(state: CrisisState) -> CrisisState:
    """
    Pause obligatoire entre AgentVeille et AgentStratège.
    Présente l'analyse à l'équipe et attend une validation manuelle.
    """
    print("\n" + "=" * 60)
    print("HUMAN GATE — VALIDATION REQUISE AVANT GÉNÉRATION DE RÉPONSE")
    print("=" * 60)
    narratives = state.get("narratives") or {}
    alerts = state.get("alerts") or {}
    print(f"  Narratif dominant : {narratives.get('narratif_dominant', 'N/A')}")
    print(f"  Répartition       : {narratives.get('repartition', {})}")
    print(f"  Niveau d'alerte   : {alerts.get('alert_level', 'N/A')}")
    print(f"  Résumé            : {alerts.get('summary', 'N/A')}")
    print("=" * 60)

    human_input = interrupt({
        "message": "Validez-vous l'analyse avant de générer des réponses ? (yes/no)",
        "narratives": narratives,
        "alerts": alerts,
    })

    state["human_approved"] = str(human_input).strip().lower() in ("yes", "oui", "y", "o")
    return state


# ── Sauvegarde des outputs ────────────────────────────────────────────────────

def save_outputs(state: CrisisState) -> CrisisState:
    """Sauvegarde tous les outputs JSON dans outputs/."""
    os.makedirs("outputs", exist_ok=True)
    run_id = state.get("run_id", "run")
    for key, filename in [
        ("narratives",       f"narratives_{run_id}.json"),
        ("alerts",           f"alerts_{run_id}.json"),
        ("strategy_options", f"strategy_{run_id}.json"),
        ("draft_response",   f"drafts_{run_id}.json"),
    ]:
        if state.get(key):
            with open(f"outputs/{filename}", "w", encoding="utf-8") as f:
                json.dump(state[key], f, ensure_ascii=False, indent=2)
    print(f"[save_outputs] Outputs dans outputs/ (run_id={run_id})")
    return state


# ── Assemblage du graphe ──────────────────────────────────────────────────────

def build_graph():
    """Construit et compile le StateGraph LangGraph."""
    graph = StateGraph(CrisisState)

    graph.add_node("analyste",     run_analyste)
    graph.add_node("veille",       run_veille)
    graph.add_node("human_gate",   human_gate)
    graph.add_node("stratege",     run_stratege)
    graph.add_node("redacteur",    run_redacteur)
    graph.add_node("save_outputs", save_outputs)

    graph.set_entry_point("analyste")
    graph.add_edge("analyste",     "veille")
    graph.add_edge("veille",       "human_gate")
    graph.add_edge("human_gate",   "stratege")
    graph.add_edge("stratege",     "redacteur")
    graph.add_edge("redacteur",    "save_outputs")
    graph.add_edge("save_outputs", END)

    return graph.compile()


# ── Initialisation de l'état ──────────────────────────────────────────────────

def init_state(df: pd.DataFrame, corpus_config: dict) -> CrisisState:
    return CrisisState(
        raw_df=df,
        # Échantillon de 500 tweets pour les agents LLM (tri chronologique conservé)
        # Ajuster selon les résultats de l'exploration J1
        tweets_sample=df.sample(min(500, len(df)), random_state=42),
        corpus_config=corpus_config,
        narratives=None,
        alerts=None,
        human_approved=False,
        strategy_options=None,
        draft_response=None,
        run_id=str(uuid.uuid4())[:8],
        errors=[],
    )


# ── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    corpus_config = {
        "evenement": "Affaire Ultia x CNC — tempête virale sur X",
        "periode": "mars-avril 2026",
        "mots_cles": ["ultia", "cnc", "cnc_talent", "cncinema"],
    }

    df = load_corpus("Dataset/data.xlsx")
    state = init_state(df, corpus_config)

    app = build_graph()
    final_state = app.invoke(state)
    print("Pipeline terminé.")
