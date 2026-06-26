import uuid
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas.requests import VeilleRequest
from src.schemas.responses import VeilleResponse

from src.tools.corpus_loader import load_corpus

from src.pipeline.session_store import save_state
from src.pipeline.state import CrisisState

from src.agents.veille import run_veille
from src.agents.analyste import run_analyste
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
