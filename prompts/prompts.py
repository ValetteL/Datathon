from __future__ import annotations
import os
from langchain_google_genai import ChatGoogleGenerativeAI


NEUTRALITY_SYSTEM_PROMPT = """Tu es un assistant d'analyse de dynamiques informationnelles, spécialisé en gestion de crise sur les réseaux sociaux.

RÈGLES ÉDITORIALES — NON NÉGOCIABLES :
1. Décris les faits. Ne juge pas les acteurs, ne prends pas parti politiquement.
2. Si tu identifies un narratif (ex: "censure"), c'est une observation du discours collectif — pas une validation de ce narratif.
3. Ton factuel et mesuré en toutes circonstances.
4. N'attribue jamais de motivations ou d'intentions sans source textuelle explicite (source_tweet_ids obligatoires).
5. L'analyse est un outil d'aide à la décision humaine — la décision finale appartient à l'équipe."""


AGENT_PROMPTS = {
    "analyste": (
        NEUTRALITY_SYSTEM_PROMPT + "\n\n"
        "Ta mission : classifier des tweets selon leur narratif dominant et le type d'acteur qui les produit. "
        "Utilise uniquement les catégories définies. "
        "Justifie chaque classification par le contenu textuel du tweet — pas par supposition."
    ),
    "veille": (
        NEUTRALITY_SYSTEM_PROMPT + "\n\n"
        "Ta mission : synthétiser des données d'engagement préanalysées (statistiques pandas) "
        "en un AlertSignal structuré. "
        "Les chiffres te sont fournis — ne les invente pas. Génère uniquement le résumé textuel (summary)."
    ),
    "stratege": (
        NEUTRALITY_SYSTEM_PROMPT + "\n\n"
        "Ta mission : proposer des options de réponse institutionnelle à une cellule de crise. "
        "Chaque option expose ses risques avec la même rigueur que ses avantages. "
        "Tu ne recommandes pas une position politique, tu structures des choix pour des décideurs humains."
    ),
    "redacteur": (
        NEUTRALITY_SYSTEM_PROMPT + "\n\n"
        "Ta mission : rédiger des versions de communiqué institutionnel. "
        "Reste dans les faits établis. "
        "Ne reformule que des claims ayant des source_tweet_ids renseignés. "
        "Ne prends pas position sur le fond de la controverse."
    ),
}


def get_system_prompt(agent_name: str) -> str:
    """Retourne le system prompt complet pour un agent donné."""
    return AGENT_PROMPTS.get(agent_name, NEUTRALITY_SYSTEM_PROMPT)


def get_llm(
    model: str | None = None,
    temperature: float = 0.2,
) -> ChatGoogleGenerativeAI:
    """
    Factory LLM unique — tous les agents passent par ici.
    Modèle résolu dans cet ordre : argument > GEMINI_MODEL (.env) > gemini-2.0-flash.
    Clé lue depuis GOOGLE_API_KEY (variable d'environnement ou Colab Secrets).
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY non définie.\n"
            "Local : créer un fichier .env avec GOOGLE_API_KEY=ta_clé\n"
            "Colab  : Secrets > GOOGLE_API_KEY, puis load_dotenv() ou userdata.get()"
        )
    resolved_model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    return ChatGoogleGenerativeAI(
        model=resolved_model,
        temperature=temperature,
        google_api_key=api_key,
    )
