import json
from typing import Any

import httpx

from app.config import settings


def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    """Low-level call to Ollama Cloud. temperature=0 for determinism."""
    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        headers={"Authorization": f"Bearer {settings.ollama_api_key}"},
        json={
            "model": settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {"temperature": 0},
            "stream": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _safe_json(raw: str) -> dict[str, Any] | None:
    """Strip common markdown-fence noise before parsing; never trust raw text."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, TypeError):
        return None


def classify_category(user_message: str, valid_categories: list[dict[str, str]]) -> str:
    """
    valid_categories: [{"key": "dining_table", "description": "..."}, ...]
    Returns a category key that is GUARANTEED to be one of valid_categories, or 'unknown'.
    """
    options_text = "\n".join(f'- {c["key"]}: {c["description"]}' for c in valid_categories)
    system_prompt = (
        "You classify a customer's request into exactly one category key from the list below. "
        "Respond with ONLY raw JSON, no markdown, no explanation, in this exact shape: "
        '{"category": "<key>"}. '
        'If nothing fits, respond {"category": "unknown"}.\n\n'
        f"Valid categories:\n{options_text}"
    )
    try:
        parsed = _safe_json(_call_ollama(system_prompt, user_message))
    except (httpx.HTTPError, KeyError):
        return "unknown"
    category = parsed.get("category", "unknown") if parsed else "unknown"

    valid_keys = {c["key"] for c in valid_categories}
    # Hard validation: never trust the model's output directly, even if it looks right.
    return category if category in valid_keys else "unknown"


def extract_field(
    user_message: str,
    question_key: str,
    answer_type: str,
    enum_options: list[str] | None,
) -> str | None:
    """
    Extracts a single structured value from free text.
    Returns a validated string value, or None if it can't be confidently/safely extracted.
    """
    constraint = ""
    if answer_type == "enum" and enum_options:
        constraint = f" The value MUST be exactly one of: {enum_options}."
    elif answer_type == "number":
        constraint = " The value MUST be a plain number, no units or words."

    system_prompt = (
        f"Extract the value for '{question_key}' from the customer's message.{constraint} "
        'Respond with ONLY raw JSON in this exact shape: {"value": "<extracted value>"}. '
        'If you cannot confidently extract it, respond {"value": null}.'
    )
    try:
        parsed = _safe_json(_call_ollama(system_prompt, user_message))
    except (httpx.HTTPError, KeyError):
        return None
    if not parsed:
        return None

    value = parsed.get("value")
    if value is None:
        return None

    # Re-validate against our own rules — the model's constraint-following is not guaranteed.
    if answer_type == "enum" and enum_options and str(value) not in enum_options:
        return None
    if answer_type == "number":
        try:
            float(value)
        except (ValueError, TypeError):
            return None

    return str(value)


def narrate_list(category_name: str, items: list[dict[str, Any]]) -> str:
    """
    Turns an already DB-assembled list into a short friendly intro.
    The model is instructed not to add/remove/rename items — it only phrases what's given.
    This step is cosmetic; if it fails, callers should fall back to a static message.
    """
    items_text = "\n".join(f'- {i["name"]} x{i["quantity"]} {i["unit"]}' for i in items)
    system_prompt = (
        "You are a friendly retail assistant. Write ONLY a short, warm 2-3 sentence intro "
        "for a shopping list that will be displayed separately below your reply. "
        "Do NOT list, repeat, or restate any item names, quantities, or the words "
        "'Category:' / 'Items:' from the input — the list is already shown to the customer "
        "elsewhere. Your entire response must be just the intro sentences, nothing else."
    )
    fallback = f"Here's everything you'll need for your {category_name.lower()}:"
    try:
        result = _call_ollama(system_prompt, f"Category: {category_name}\nItems:\n{items_text}").strip()
    except (httpx.HTTPError, KeyError):
        return fallback

    # Defensive: even if the model ignores the instruction and echoes the item list,
    # cut it off at the first sign of a leaked list rather than showing raw data.
    for marker in ("Category:", "Items:", "- "):
        idx = result.find(marker)
        if idx != -1:
            result = result[:idx].strip()

    return result if result else fallback