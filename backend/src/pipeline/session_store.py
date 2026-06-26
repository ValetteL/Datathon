from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipeline.state import CrisisState

SESSIONS_DIR = Path(__file__).parent.parent.parent / "outputs"
SESSIONS_DIR.mkdir(exist_ok=True)

# Les DataFrames ne sont pas sérialisables — on les exclut du fichier disque.
_NON_SERIALIZABLE = {"raw_df", "tweets_sample"}

_store: dict = {}


class _SafeEncoder(json.JSONEncoder):
    """Sérialise les types numpy/pandas courants en types Python natifs."""

    def default(self, obj):
        try:
            import numpy as np

            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        try:
            import pandas as pd

            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
        except ImportError:
            pass
        return super().default(obj)


_RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _validate_run_id(run_id: str) -> None:
    if not _RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"run_id invalide : {run_id!r}")


def _session_path(run_id: str) -> Path:
    _validate_run_id(run_id)
    p = (SESSIONS_DIR / f"session_{run_id}.json").resolve()
    if SESSIONS_DIR.resolve() not in p.parents:
        raise ValueError(f"run_id invalide : {run_id!r}")
    return p


def _serializable_state(state: dict) -> dict:
    return {k: v for k, v in state.items() if k not in _NON_SERIALIZABLE}


def _write_to_disk(run_id: str) -> None:
    meta = _store[run_id]
    payload = {
        "run_id": run_id,
        "created_at": meta["created_at"],
        "status": meta["status"],
        "state": _serializable_state(meta["state"]),
    }
    tmp = _session_path(run_id).with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, cls=_SafeEncoder))
    tmp.replace(_session_path(run_id))


def _load_all_sessions() -> None:
    """Restaure les sessions persistées au démarrage du serveur."""
    for path in sorted(SESSIONS_DIR.glob("session_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            run_id = data.get("run_id") or path.stem.removeprefix("session_")
            _validate_run_id(run_id)  # rejette tout run_id suspect lu depuis le disque
            if run_id not in _store:
                _store[run_id] = {
                    "created_at": data.get("created_at"),
                    "status": data.get("status", "idle"),
                    "state": data.get("state", {}),
                }
        except Exception:
            pass  # fichier corrompu ou run_id invalide — ignoré silencieusement


def save_state(run_id: str, state: dict) -> None:
    if run_id not in _store:
        _store[run_id] = {"created_at": datetime.now().isoformat()}
    _store[run_id]["state"] = state
    _store[run_id]["status"] = _compute_status(state)
    _write_to_disk(run_id)


def get_state(run_id: str) -> CrisisState:
    if run_id not in _store:
        raise KeyError(f"run_id inconnu : {run_id}")
    return _store[run_id]["state"]


def get_session(run_id: str) -> dict:
    if run_id not in _store:
        raise KeyError(f"run_id inconnu : {run_id}")
    return _store[run_id]


def mark_rejected(run_id: str) -> None:
    if run_id not in _store:
        raise KeyError(f"run_id inconnu : {run_id}")
    _store[run_id]["status"] = "rejected"
    _write_to_disk(run_id)


def list_sessions() -> list:
    return sorted(
        [
            {
                "run_id": rid,
                "status": meta["status"],
                "alert_level": (
                    meta["state"].get("alerts", {}).get("alert_level")
                    if meta["state"].get("alerts")
                    else None
                ),
                "created_at": meta["created_at"],
            }
            for rid, meta in _store.items()
            if meta["state"].get("alerts") is not None
        ],
        key=lambda x: x["created_at"] or "",
        reverse=True,
    )


def _compute_status(state: dict) -> str:
    if state.get("draft_response"):
        return "complete"
    if state.get("strategy_options"):
        return "stratege_done"
    if state.get("human_approved") and state.get("alerts"):
        return "awaiting_stratege"
    if state.get("alerts"):
        return "awaiting_human"
    if state.get("narratives"):
        return "analyste_done"
    return "idle"


# Chargement au démarrage du module
_load_all_sessions()
