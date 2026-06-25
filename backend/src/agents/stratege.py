from langchain_core.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel, Field
from pipeline.state import CrisisState
from prompts.prompts import get_llm, get_system_prompt


class ResponseOption(BaseModel):
    option_id: str
    titre: str
    description: str
    tonalite: str = Field(description="prudent | equilibre | assertif")
    risques: list[str]
    source_tweet_ids: list[str]


class StrategyOptions(BaseModel):
    options: list[ResponseOption]
    option_recommandee: str
    justification: str
    source_tweet_ids: list[str]


def run_stratege(state: CrisisState) -> CrisisState:
    assert state["human_approved"], "HumanGate non validé - AgentStratège bloqué."

    narratives = state["narratives"] or {}
    alerts = state["alerts"] or {}
    config = state["corpus_config"]

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", get_system_prompt("stratege")),
            (
                "human",
                (
                    "Contexte : {evenement}\n\n"
                    "Narratif dominant = {narratif_dominant}\n"
                    "Répartition des narratifs = {repartition}\n"
                    "Niveau d'alerte : {alert_level}\n"
                    "Résumé de la crise : {alert_summary}\n\n"
                    "Propose 3 options de réponse institutionnelle (prudent/équilibré/assertif) avec leurs risques. Chaque option doit citer des source_tweet_ids."
                ),
            ),
        ]
    )

    result: StrategyOptions = (prompt | llm.with_structured_output(StrategyOptions)).invoke(
        {
            "evenement": config.get("evenement", ""),
            "narratif_dominant": narratives.get("narratif_dominant", ""),
            "repartition": str(narratives.get("repartition", {})),
            "alert_level": alerts.get("alert_level", ""),
            "alert_summary": alerts.get("summary", ""),
        }
    )

    state["strategy_options"] = result.model_dump()
    return state
