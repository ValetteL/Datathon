corpus_config: dict = {
    "evenement": "Affaire Ultia x CNC",
    "periode": "mars-avril 2026",
    "narratifs": ["censure", "copinage", "defense_ultia", "defense_cnc", "autre"],
    "acteurs": ["media", "militant", "influenceur", "anonyme", "institution", "coordonne_bot"],
    "few_shot": (
        "Exemples de calibration :\n"
        "- \"Ils censurent encore une fois la vérité, c'est inadmissible\" → narratif=censure, acteur_type=militant\n"
        "- \"Tout le monde savait, c'est encore du copinage entre les mêmes\" → narratif=copinage, acteur_type=anonyme\n"
        "- \"Le CNC applique simplement le règlement, rien d'anormal ici\" → narratif=defense_cnc, acteur_type=institution\n"
        "- \"Ultia n'a rien fait de mal, on s'acharne sur eux sans preuve\" → narratif=defense_ultia, acteur_type=influenceur\n"
        "- \"Je n'ai pas d'avis tranché, attendons d'en savoir plus\" → narratif=autre, acteur_type=anonyme\n"
        "- Compte postant 40 fois en 10 min avec textes quasi-identiques → acteur_type=coordonne_bot"
    ),
}
