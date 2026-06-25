import uuid
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tools.corpus_loader import load_corpus
from pipeline.state import CrisisState
from agents.veille import run_veille
from agents.stratege import run_stratege

console = Console()
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

# --- Veille ---
console.rule("[bold cyan]Agent Veille[/bold cyan]")
state = run_veille(state)
alerts = state["alerts"] or {}

level_color = {
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
}
color = level_color.get(alerts["alert_level"], "white")

console.print(
    Panel(
        f"[{color}]Niveau : {alerts['alert_level'].upper()}[/{color}]\n\n"
        f"{alerts['summary']}\n\n"
        f"[dim]Tweets viraux : {alerts['threshold_breaches']['viral_tweets_count']} | "
        f"Pic journalier : {alerts['threshold_breaches']['max_daily_volume']} tweets[/dim]",
        title="Résultat Veille",
        border_style=color,
    )
)

table = Table(title="Pics détectés", show_header=True, header_style="bold magenta")
table.add_column("Date")
table.add_column("Volume", justify="right")
table.add_column("Top Shares", justify="right")
for peak in alerts["peaks"]:
    table.add_row(peak["date"], str(peak["tweet_count"]), str(peak["top_shares"]))
console.print(table)

# --- HumanGate ---
console.rule("[bold yellow]Human Gate[/bold yellow]")
reponse = console.input("[yellow]Valider l'analyse ? (oui/non) : [/yellow]")
state["human_approved"] = reponse.lower() in ("oui", "o", "yes", "y")

if not state["human_approved"]:
    console.print("[red]Analyse rejetée. Pipeline arrêté.[/red]")
    exit()

# --- Stratège ---
console.rule("[bold green]Agent Stratège[/bold green]")
state = run_stratege(state)
options = state["strategy_options"] or {}

tonalite_color = {"prudent": "blue", "equilibre": "yellow", "assertif": "red"}

for opt in options["options"]:
    color = tonalite_color.get(opt["tonalite"], "white")
    recommande = " ⭐" if opt["option_id"] == options["option_recommandee"] else ""
    console.print(
        Panel(
            f"[bold]Tonalité :[/bold] [{color}]{opt['tonalite']}[/{color}]\n\n"
            f"{opt['description']}\n\n"
            f"[dim]Risques : {' | '.join(opt['risques'])}[/dim]",
            title=f"{opt['titre']}{recommande}",
            border_style=color,
        )
    )

console.print(
    Panel(
        f"[italic]{options['justification']}[/italic]",
        title="Recommandation",
        border_style="green",
    )
)
