from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.routers import chat
from app.schemas import HealthResponse

app = FastAPI(title="Smart Product Recommendation Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "unreachable"

    llm_status = "ok"
    try:
        httpx.get(
            f"{settings.ollama_base_url}/api/tags",
            headers={"Authorization": f"Bearer {settings.ollama_api_key}"},
            timeout=5,
        ).raise_for_status()
    except Exception:
        llm_status = "unreachable"

    return HealthResponse(status="ok", database=db_status, llm=llm_status)
