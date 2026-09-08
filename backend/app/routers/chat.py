from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import ChatRequest, ChatResponse, ShoppingListItem
from app.services import llm_service, recommendation_service, session_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    state = session_service.get_session(db, req.session_id)

    # Step 1: category not yet known -> classify against DB's known categories only
    if state["category"] is None:
        categories = db.query(models.Category).all()
        cat_options = [{"key": c.key, "description": c.description} for c in categories]
        category_key = llm_service.classify_category(req.message, cat_options)

        if category_key == "unknown":
            return ChatResponse(
                session_id=req.session_id,
                reply=(
                    "I couldn't quite place that request — could you tell me a bit more, "
                    "or would you like to speak with one of our experts?"
                ),
                is_final=False,
            )

        state["category"] = category_key
        session_service.save_session(db, req.session_id, state)

        category_row = db.query(models.Category).filter_by(key=category_key).first()
        first_question = (
            db.query(models.CategoryQuestion)
            .filter_by(category_id=category_row.id)
            .order_by(models.CategoryQuestion.display_order)
            .first()
        )
        if first_question is None:
            # Category exists but has no configured questions — nothing to ask, go straight to list.
            items = recommendation_service.build_shopping_list(db, category_row.id, {})
            session_service.reset_session(db, req.session_id)
            return ChatResponse(
                session_id=req.session_id,
                reply=llm_service.narrate_list(category_row.display_name, items),
                is_final=True,
                shopping_list=[ShoppingListItem(**i) for i in items],
                category=category_row.key,
            )

        state["pending_question"] = first_question.question_key
        session_service.save_session(db, req.session_id, state)
        return ChatResponse(
            session_id=req.session_id,
            reply=llm_service.generate_question(
                category_row.display_name,
                first_question.question_key,
                first_question.answer_type,
                first_question.enum_options,
                {},
                first_question.question_text,
            ),
            is_final=False,
            category=category_key,
        )

    # Step 2: category known, mid question flow
    category_row = db.query(models.Category).filter_by(key=state["category"]).first()
    questions = (
        db.query(models.CategoryQuestion)
        .filter_by(category_id=category_row.id)
        .order_by(models.CategoryQuestion.display_order)
        .all()
    )

    pending_key = state.get("pending_question")
    if pending_key:
        current_question = next((q for q in questions if q.question_key == pending_key), None)
        if current_question is not None:
            value = llm_service.extract_field(
                req.message,
                current_question.question_key,
                current_question.answer_type,
                current_question.enum_options,
            )
            if value is None:
                state["retries"] = state.get("retries", 0) + 1
                session_service.save_session(db, req.session_id, state)
                if state["retries"] >= 3:
                    category = state["category"]
                    session_service.reset_session(db, req.session_id)
                    return ChatResponse(
                        session_id=req.session_id,
                        reply="I'm having trouble understanding — let me connect you with one of our experts.",
                        is_final=False,
                        category=category,
                    )
                return ChatResponse(
                    session_id=req.session_id,
                    reply=(
                        f"Sorry, I didn't quite catch that. "
                        f"{llm_service.generate_question(category_row.display_name, current_question.question_key, current_question.answer_type, current_question.enum_options, state['answers'], current_question.question_text)}"
                    ),
                    is_final=False,
                    category=state["category"],
                )
            state["retries"] = 0
            state["answers"][current_question.question_key] = value
            session_service.save_session(db, req.session_id, state)

    next_question = next((q for q in questions if q.question_key not in state["answers"]), None)

    if next_question is not None:
        state["pending_question"] = next_question.question_key
        session_service.save_session(db, req.session_id, state)
        return ChatResponse(
            session_id=req.session_id,
            reply=llm_service.generate_question(
                category_row.display_name,
                next_question.question_key,
                next_question.answer_type,
                next_question.enum_options,
                state["answers"],
                next_question.question_text,
            ),
            is_final=False,
            category=state["category"],
        )

    # Step 3: all answers collected -> deterministic SQL-built list, LLM only narrates
    items = recommendation_service.build_shopping_list(db, category_row.id, state["answers"])
    intro = llm_service.narrate_list(category_row.display_name, items)
    session_service.reset_session(db, req.session_id)

    return ChatResponse(
        session_id=req.session_id,
        reply=intro,
        is_final=True,
        shopping_list=[ShoppingListItem(**i) for i in items],
        category=category_row.key,
    )
