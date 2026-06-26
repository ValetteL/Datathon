import json
import os
import uuid
from time import perf_counter
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.tools.corpus_loader import load_corpus
from src.pipeline.state import CrisisState
from src.agents.veille import run_veille
from src.agents.analyste import run_analyste
from src.agents.stratege import run_stratege
from src.agents.redacteur import run_redacteur


console = Console()
load_dotenv()

df = load_corpus("./Dataset/data.xlsx")

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

console.print(f"\n[dim]Run ID : {state['run_id']}[/dim]\n")
timings: dict[str, float] = {}

# ── Agent Analyste ────────────────────────────────────────────────────────────
console.rule("[bold blue]Agent Analyste[/bold blue]")
t0 = perf_counter()
with console.status("[blue]Classification des tweets en cours…[/blue]", spinner="dots"):
    state = run_analyste(state)
timings["analyste"] = perf_counter() - t0

narratives = state["narratives"] or {}
repartition = narratives.get("repartition", {})
total = sum(repartition.values()) or 1

table_narratifs = Table(
    title="Répartition des narratifs", show_header=True, header_style="bold blue"
)
table_narratifs.add_column("Narratif")
table_narratifs.add_column("Tweets", justify="right")
table_narratifs.add_column("%", justify="right")
for narratif, count in sorted(repartition.items(), key=lambda x: -x[1]):
    table_narratifs.add_row(narratif, str(count), f"{count / total * 100:.1f}%")
console.print(table_narratifs)

console.print(
    Panel(
        f"[bold]Narratif dominant :[/bold] {narratives.get('narratif_dominant', 'N/A')}\n"
        f"[dim]{len(narratives.get('analyses', []))} tweets classifiés "
        f"en {timings['analyste']:.1f}s[/dim]",
        border_style="blue",
        expand=False,
    )
)

if state.get("errors"):
    console.print(
        f"[yellow]⚠ {len(state['errors'])} erreur(s) de batch — pipeline continue[/yellow]"
    )
    for err in state["errors"]:
        console.print(f"  [dim red]{err}[/dim red]")

# ── Agent Veille ──────────────────────────────────────────────────────────────
console.rule("[bold cyan]Agent Veille[/bold cyan]")
t0 = perf_counter()
with console.status("[cyan]Détection des pics et alertes…[/cyan]", spinner="dots"):
    state = run_veille(state)
timings["veille"] = perf_counter() - t0

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
        f"Pic journalier : {alerts['threshold_breaches']['max_daily_volume']} tweets | "
        f"{timings['veille']:.1f}s[/dim]",
        title="Résultat Veille",
        border_style=color,
    )
)

table_pics = Table(title="Pics détectés", show_header=True, header_style="bold magenta")
table_pics.add_column("Date")
table_pics.add_column("Volume", justify="right")
table_pics.add_column("Top Shares", justify="right")
for peak in alerts["peaks"]:
    table_pics.add_row(peak["date"], str(peak["tweet_count"]), str(peak["top_shares"]))
console.print(table_pics)

# ── Human Gate ────────────────────────────────────────────────────────────────
console.rule("[bold yellow]Human Gate[/bold yellow]")
reponse = console.input("[yellow]Valider l'analyse ? (oui/non) : [/yellow]")
state["human_approved"] = reponse.lower() in ("oui", "o", "yes", "y")

if not state["human_approved"]:
    console.print("[red]Analyse rejetée. Pipeline arrêté.[/red]")
    exit()

# ── Agent Stratège ────────────────────────────────────────────────────────────
console.rule("[bold green]Agent Stratège[/bold green]")
t0 = perf_counter()
with console.status(
    "[green]Génération des options de réponse…[/green]", spinner="dots"
):
    state = run_stratege(state)
timings["stratege"] = perf_counter() - t0

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
        title=f"Recommandation  [dim]({timings['stratege']:.1f}s)[/dim]",
        border_style="green",
    )
)

# ── Agent Rédacteur ───────────────────────────────────────────────────────────
console.rule("[bold magenta]Agent Rédacteur[/bold magenta]")
t0 = perf_counter()
with console.status("[magenta]Rédaction des communiqués…[/magenta]", spinner="dots"):
    state = run_redacteur(state)
timings["redacteur"] = perf_counter() - t0

drafts = state["draft_response"] or {}

for version in drafts["versions"]:
    color = tonalite_color.get(version["tonalite"], "white")
    recommande = " ⭐" if version["tonalite"] == drafts["recommandation"] else ""
    console.print(
        Panel(
            f"{version['corps']}\n\n"
            f"[bold]Call to action :[/bold] {version['call_to_action']}",
            title=f"{version['titre']}{recommande} [{version['tonalite']}]",
            border_style=color,
        )
    )

# ── Sauvegarde JSON ───────────────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
run_id = state["run_id"]
saved: list[str] = []
for key, filename in [
    ("narratives", f"narratives_{run_id}.json"),
    ("alerts", f"alerts_{run_id}.json"),
    ("strategy_options", f"strategy_{run_id}.json"),
    ("draft_response", f"drafts_{run_id}.json"),
]:
    if state.get(key):
        path = f"outputs/{filename}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state[key], f, ensure_ascii=False, indent=2)
        saved.append(path)

# ── Récap final ───────────────────────────────────────────────────────────────
console.rule("[bold white]Récapitulatif[/bold white]")

recap = Table(show_header=False, box=None, padding=(0, 2))
recap.add_column(style="dim")
recap.add_column()
recap.add_row("Run ID", state["run_id"])
recap.add_row("Tweets analysés", str(len(narratives.get("analyses", []))))
recap.add_row("Narratif dominant", narratives.get("narratif_dominant", "N/A"))
recap.add_row("Niveau d'alerte", alerts.get("alert_level", "N/A").upper())
recap.add_row("Option recommandée", options.get("option_recommandee", "N/A"))
recap.add_row("Tonalité recommandée", drafts.get("recommandation", "N/A"))
recap.add_row(
    "Temps total",
    f"{sum(timings.values()):.1f}s  "
    f"[dim](analyste {timings['analyste']:.0f}s · veille {timings['veille']:.0f}s · "
    f"stratège {timings['stratege']:.0f}s · rédacteur {timings['redacteur']:.0f}s)[/dim]",
)

console.print(Panel(recap, title="Pipeline terminé", border_style="white"))

if saved:
    console.print(f"[dim]Outputs sauvegardés : {', '.join(saved)}[/dim]\n")
