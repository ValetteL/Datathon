import uuid
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas.requests import StrategeRequest, VeilleRequest, RedacteurRequest
from src.schemas.responses import (
    VeilleResponse,
    StrategeResponse,
    RedacteurResponse,
    SessionSummary,
    SessionDetail,
)

from src.tools.corpus_loader import load_corpus

from src.pipeline.session_store import (
    get_state,
    save_state,
    list_sessions,
    get_session,
)
from src.pipeline.state import CrisisState

from src.agents.veille import run_veille
from src.agents.stratege import run_stratege
from src.agents.redacteur import run_redacteur

load_dotenv()

df_global = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global df_global
    df_global = load_corpus("Dataset/data.xlsx")
    yield


app = FastAPI(title="Datathon", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "tweets": len(df_global) if df_global is not None else 0}


@app.post("/analyse/veille", response_model=VeilleResponse)
def analyse_veille(body: VeilleRequest):
    run_id = str(uuid.uuid4())[:8]

    if df_global is None:
        raise HTTPException(status_code=500, detail="Aucune données chargé.")

    state = CrisisState(
        raw_df=df_global,
        tweets_sample=df_global.sample(
            min(body.sample_size, len(df_global)), random_state=42
        ),
        corpus_config=body.corpus_config,
        narratives=body.narratives_mock,
        alerts=None,
        human_approved=False,
        strategy_options=None,
        draft_response=None,
        run_id=run_id,
        errors=[],
    )

    try:
        state = run_veille(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    save_state(run_id, dict(state))

    alerts = state["alerts"]
    if alerts is None:
        raise HTTPException(
            status_code=500, detail="AgentVeille n'a produit aucune alerte."
        )

    return VeilleResponse(
        run_id=run_id,
        is_alert=alerts["is_alert"],
        alert_level=alerts["alert_level"],
        peaks=alerts["peaks"],
        summary=alerts["summary"],
        threshold_breaches=alerts["threshold_breaches"],
        is_mock=body.narratives_mock is not None,
    )


@app.post("/analyse/stratege", response_model=StrategeResponse)
def analyse_stratege(body: StrategeRequest):
    if not body.humain_approved:
        raise HTTPException(
            status_code=403, detail="human_approved est false — pipeline bloqué."
        )

    try:
        state = get_state(body.run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"run_id inconnu : {body.run_id}")

    state["human_approved"] = True

    try:
        state = run_stratege(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    save_state(body.run_id, dict(state))

    options = state["strategy_options"]
    if options is None:
        raise HTTPException(
            status_code=500, detail="AgentStratège n'a produit aucune option."
        )

    return StrategeResponse(
        run_id=body.run_id,
        options=options["options"],
        option_recommandee=options["option_recommandee"],
        justification=options["justification"],
    )


@app.post("/analyse/redacteur", response_model=RedacteurResponse)
def analyse_redacteur(body: RedacteurRequest):
    try:
        state = get_state(body.run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"run_id inconnu : {body.run_id}")

    if state.get("strategy_options") is None:
        raise HTTPException(
            status_code=400, detail="AgentStratège non exécuté sur ce run_id."
        )

    try:
        state = run_redacteur(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    save_state(body.run_id, dict(state))

    drafts = state["draft_response"]
    if drafts is None:
        raise HTTPException(
            status_code=500, detail="AgentRedacteur n'a produit aucun draft."
        )

    return RedacteurResponse(
        run_id=body.run_id,
        versions=drafts["versions"],
        recommandation=drafts["recommandation"],
    )


@app.get("/sessions", response_model=list[SessionSummary])
def sessions_list():
    return list_sessions()


@app.get("/sessions/{run_id}", response_model=SessionDetail)
def session_detail(run_id: str):
    try:
        meta = get_session(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"run_id inconnu : {run_id}")

    state = meta["state"]

    return SessionDetail(
        run_id=run_id,
        status=meta["status"],
        is_mock=state.get("narratives") is not None,
        alerts=state.get("alerts"),
        strategy_options=state.get("strategy_options"),
        draft_response=state.get("draft_response"),
    )
