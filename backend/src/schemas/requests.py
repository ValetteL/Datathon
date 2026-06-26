from pydantic import BaseModel
from src.utils.config import corpus_config


class VeilleRequest(BaseModel):
    sample_size: int = 200
    corpus_config: dict = corpus_config
    narratives_mock: dict | None = None


class StrategeRequest(BaseModel):
    run_id: str
    humain_approved: bool


class RedacteurRequest(BaseModel):
    run_id: str
