import os
import uuid
from dotenv import load_dotenv
from tools.corpus_loader import load_corpus
from pipeline.state import CrisisState
from agents.veille import run_veille
from agents.stratege import run_stratege

load_dotenv()

df = load_corpus("Dataset/data.xlsx")

state = CrisisState(
    raw_df=df,
    tweets_sample=df.sample(200, random_state=42),
    corpus_config={"evenement": "Affaire Ultia x CNC", "periode": "mars-avril 2026"},
    narratives=None,
    alerts=None,
    human_approved=False,
    strategy_options=None,
    draft_response=None,
    run_id=str(uuid.uuid4())[:8],
    errors=[],
)

print("--- AgentVeille ---")
state = run_veille(state)
print(state["alerts"])

print("\n--- HumanGate ---")
reponse = input("Valider l'analyse ? (oui/non) : ")
state["human_approved"] = reponse.lower() in ("oui", "o", "yes", "y")

print("\n--- AgentStratège ---")
state = run_stratege(state)
print(state["strategy_options"])
