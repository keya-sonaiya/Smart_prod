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
        constraint = (
            f" The canonical enum values are exactly: {enum_options}. "
            "Parse the customer's wording and return the matching canonical value, "
            "normalizing harmless differences in case, spaces, hyphens, and punctuation "
            "(for example, 'high end' and 'highend' both mean 'high-end')."
        )
    elif answer_type == "number":
        constraint = (
            " Extract the numeric value even when the customer includes units or common "
            "number words; return only the number."
        )
    elif answer_type == "text":
        constraint = (
            " Preserve the useful meaning of free text and normalize common informal "
            "phrasing. For dimensions, inputs such as '6 x 7 ft', '6x7', or '6 7' "
            "mean '6ft x 7ft'; do not reject them just because units or spacing vary."
        )

    system_prompt = (
        f"Extract the value for '{question_key}' from the customer's message. "
        f"The raw customer input is: {user_message!r}."
        f"{constraint} "
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
    if answer_type == "enum" and enum_options:
        normalized = "".join(character for character in str(value).lower() if character.isalnum())
        matching_option = next(
            (
                option
                for option in enum_options
                if "".join(character for character in option.lower() if character.isalnum()) == normalized
            ),
            None,
        )
        if matching_option is None:
            return None
        return matching_option
    if answer_type == "number":
        try:
            float(value)
        except (ValueError, TypeError):
            return None

    return str(value)


def generate_question(
    category_name: str,
    question_key: str,
    answer_type: str,
    enum_options: list[str] | None,
    prior_answers: dict[str, str],
    fallback_text: str,
) -> str:
    """Generate wording without changing the DB-defined field or answer contract."""
    context = ", ".join(f"{key}: {value}" for key, value in prior_answers.items()) or "nothing yet"
    if answer_type == "enum" and enum_options:
        constraint = (
            f" The answer MUST be exactly one of these canonical values: {enum_options}."
        )
    elif answer_type == "number":
        constraint = (
            " Ask for a numeric answer only. Say 'how many' or 'what number', and do not "
            "replace the number with a qualitative description or a different concept."
        )
    elif answer_type == "text":
        constraint = (
            " Ask for the requested free-text value directly. If this is a size or dimension, "
            "give a concise example such as '6 x 7 ft'."
        )
    else:
        constraint = ""
    system_prompt = (
        f"You are a helpful retail expert helping a customer with a {category_name} project. "
        f"So far they've told you: {context}. "
        f"Ask ONE natural, friendly follow-up question for the field '{question_key}'. "
        f"The field's answer type is '{answer_type}'. Do not ask about any other field "
        f"and do not rename or reinterpret this field.{constraint} "
        "Respond with ONLY the question text, nothing else."
    )
    try:
        result = _call_ollama(system_prompt, "Ask the next question.").strip()
    except (httpx.HTTPError, KeyError):
        return fallback_text
    return result or fallback_text


def choose_next_question(
    category_name: str,
    questions: list[dict[str, Any]],
    prior_answers: dict[str, str],
) -> str | None:
    """Choose a valid remaining question key, or null when no question is needed."""
    question_text = "\n".join(
        f'- {question["question_key"]} ({question["answer_type"]}): {question.get("enum_options") or "free text"}'
        for question in questions
    )
    answers_text = json.dumps(prior_answers, sort_keys=True) if prior_answers else "{}"
    system_prompt = (
        f"You are guiding a customer through a {category_name} recommendation. "
        "Decide whether another answer is needed before generating the shopping list. "
        "Choose exactly one question_key from the remaining list when its answer could "
        "improve, condition, or complete the recommendation. Return null only when none "
        "of the remaining questions is useful or the customer has already provided its "
        "meaning. Preserve the listed question order: choose the earliest useful remaining "
        "question, and skip earlier questions only when they are clearly unnecessary. "
        "Never invent a question key. Respond with ONLY raw JSON in this shape: "
        '{"question_key": "<key>"} or {"question_key": null}.\n\n'
        f"Remaining questions:\n{question_text}\n"
        f"Answers already collected: {answers_text}"
    )
    try:
        parsed = _safe_json(_call_ollama(system_prompt, "Choose the next question."))
    except (httpx.HTTPError, KeyError):
        return questions[0]["question_key"] if questions else None
    if not parsed or parsed.get("question_key") is None:
        return None

    selected_key = parsed.get("question_key")
    valid_keys = {question["question_key"] for question in questions}
    return selected_key if selected_key in valid_keys else (questions[0]["question_key"] if questions else None)


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