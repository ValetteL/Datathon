from datetime import datetime


_store: dict = {}


def save_state(run_id: str, state: dict) -> None:
    if run_id not in _store:
        _store[run_id] = {"created_at": datetime.now().isoformat()}
    _store[run_id]["state"] = state
    _store[run_id]["status"] = _compute_status(state)


def get_state(run_id: str) -> dict:
    if run_id not in _store:
        raise KeyError(f"run_id inconnu : {run_id}")
    return _store[run_id]["state"]


def get_session(run_id: str) -> dict:
    if run_id not in _store:
        raise KeyError(f"run_id inconnnu : {run_id}")
    return _store[run_id]


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
    return "idle"
