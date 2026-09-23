from __future__ import annotations

from collections import Counter
from typing import Any

from .catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract
from .registry import registry


def binding_status_report() -> dict[str, Any]:
    """Return a deterministic, non-LLM readiness report for the registered catalog."""
    definitions = registry.list()
    canonical_ids = {d.id.upper() for d in definitions}
    checks = []
    for exercise_id, contract in sorted(EXACT_BINDINGS.items()):
        if exercise_id not in canonical_ids:
            continue
        check = check_binding_contract(contract)
        checks.append({
            "exercise_id": exercise_id,
            "status": check.status,
            "callable": f"{check.module}.{check.callable_name}",
            "reason": check.reason,
        })
    counts = Counter(item["status"] for item in checks)
    exact_ids = {item["exercise_id"] for item in checks}
    return {
        "registered_exercises": len(definitions),
        "exact_binding_contracts": len(checks),
        "verified_exact_bindings": counts.get("VERIFIED", 0),
        "blocked_exact_bindings": counts.get("BLOCKED", 0),
        "without_exact_binding": len(canonical_ids - exact_ids),
        "checks": checks,
    }
