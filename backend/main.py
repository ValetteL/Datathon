from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.tools.corpus_loader import load_corpus


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
