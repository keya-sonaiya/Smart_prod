from typing import Any

from sqlalchemy.orm import Session

from app import models

# Whitelisted quantity formulas only — never eval() user- or LLM-influenced strings.
_NAMED_FORMULAS = {
    "seating": lambda answers: int(float(answers.get("seating", 1))),
    "seating/2": lambda answers: max(1, int(float(answers.get("seating", 2))) // 2),
}


def _resolve_quantity(formula: str | None, answers: dict[str, Any]) -> int:
    if not formula:
        return 1
    formula = formula.strip()
    if formula.isdigit():
        return int(formula)
    resolver = _NAMED_FORMULAS.get(formula)
    if resolver:
        try:
            return resolver(answers)
        except (TypeError, ValueError):
            return 1
    return 1


def _condition_matches(condition_json: dict[str, Any] | None, answers: dict[str, Any]) -> bool:
    if not condition_json:
        return True
    return all(str(answers.get(k)) == str(v) for k, v in condition_json.items())


def build_shopping_list(db: Session, category_id: int, answers: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Pure DB lookup. Every returned item corresponds to a real product_relationships row
    that matched this category and the customer's answers — nothing here is LLM-generated.
    """
    relationships = (
        db.query(models.ProductRelationship)
        .filter(models.ProductRelationship.category_id == category_id)
        .all()
    )

    result: list[dict[str, Any]] = []
    for rel in relationships:
        if not _condition_matches(rel.condition_json, answers):
            continue
        product = db.query(models.Product).get(rel.product_id)
        if product is None:
            continue
        result.append(
            {
                "name": product.name,
                "quantity": _resolve_quantity(rel.quantity_formula, answers),
                "unit": product.unit or "pcs",
                "relation_type": rel.relation_type,
            }
        )
    return result
