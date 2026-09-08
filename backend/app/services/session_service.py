from typing import Any

from sqlalchemy.orm import Session

from app import models


def _new_state() -> dict[str, Any]:
    return {"category": None, "answers": {}, "pending_question": None, "retries": 0}


def get_session(db: Session, session_id: str) -> dict[str, Any]:
    row = db.get(models.ConversationSession, session_id)
    if row is None:
        state = _new_state()
        db.add(models.ConversationSession(session_id=session_id, state=state))
        db.commit()
        return state
    return dict(row.state)


def save_session(db: Session, session_id: str, state: dict[str, Any]) -> None:
    row = db.get(models.ConversationSession, session_id)
    if row is None:
        db.add(models.ConversationSession(session_id=session_id, state=state))
    else:
        row.state = state
    db.commit()


def reset_session(db: Session, session_id: str) -> None:
    row = db.get(models.ConversationSession, session_id)
    if row is not None:
        db.delete(row)
        db.commit()
