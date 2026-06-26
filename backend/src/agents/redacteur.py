from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.pipeline.state import CrisisState
from src.prompts.prompts import get_llm, get_system_prompt


class DraftVersion(BaseModel):
    tonalite: str = Field(description="prudent | equilibre | assertif")
    titre: str
    corps: str
    call_to_action: str
    source_tweet_ids: list[str]


class DraftCommunique(BaseModel):
    versions: list[DraftVersion]
    recommandation: str = Field(description="Tonalité recommandée parmi les 3 versions")
    source_tweet_ids: list[str]


def run_redacteur(state: CrisisState) -> CrisisState:
    strategy = state["strategy_options"] or {}
    narratives = state["narratives"] or {}
    config = state["corpus_config"]

    options_text = "\n".join(
        f"- [{opt['option_id']} / {opt['tonalite']}] {opt['titre']} : {opt['description']}"
        for opt in strategy.get("options", [])
    )

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", get_system_prompt("redacteur")),
            (
                "human",
                (
                    "Contexte : {evenement}\n"
                    "Narratif dominant à adresser : {narratif_dominant}\n\n"
                    "Options stratégiques validées :\n{options}\n\n"
                    "Rédige 3 versions de communiqué (prudent, équilibré, assertif). "
                    "Chaque version doit être factuelle, citer des source_tweet_ids, "
                    "et ne pas prendre position politique."
                ),
            ),
        ]
    )

    result: DraftCommunique = (
        prompt | llm.with_structured_output(DraftCommunique)
    ).invoke(
        {
            "evenement": config.get("evenement", ""),
            "narratif_dominant": narratives.get("narratif_dominant", ""),
            "options": options_text,
        }
    )

    state["draft_response"] = result.model_dump()
    return state
