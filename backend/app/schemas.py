from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2000)


class ShoppingListItem(BaseModel):
    name: str
    quantity: int
    unit: str
    relation_type: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    is_final: bool
    shopping_list: list[ShoppingListItem] | None = None
    category: str | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
