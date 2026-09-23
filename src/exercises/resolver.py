from __future__ import annotations
from .registry import registry

def resolve_exercise(query: str, exercise_id: str | None = None):
    if exercise_id:
        return registry.get(exercise_id)
    q = query.lower().strip()
    if any(term in q for term in ("sales trend", "sales performance", "sales growth", "sales decline", "sales trend analysis")):
        return registry.get("SAL-008")
    raise KeyError("No registered exercise matched the query. Supply an exercise_id or use a supported intent.")
