from typing import Any


_sessions: dict[str, dict[str, Any]] = {}


def get_session(session_id: str) -> dict[str, Any]:
    return _sessions.setdefault(
        session_id,
        {"category": None, "answers": {}, "pending_question": None},
    )


def save_session(session_id: str, state: dict[str, Any]) -> None:
    _sessions[session_id] = state


def reset_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
