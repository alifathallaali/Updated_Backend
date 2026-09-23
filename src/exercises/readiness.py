from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .binding_status import binding_status_report
from .catalog.capability_audit import audit_capabilities
from .registry import registry


def exercise_readiness_report() -> dict[str, Any]:
    """Conservative rollout tiers for the current runtime catalog.

    TIER_1_EXECUTABLE: exact semantic contract exists and verifies at runtime.
    TIER_2_CANDIDATE: relevant deterministic capability exists but exact semantics are unverified.
    TIER_3_UNMAPPED: no validated deterministic capability is mapped.
    COMPOSITE: orchestration definition; readiness is evaluated through child exercises.
    """
    definitions = registry.list()
    exact = binding_status_report()
    exact_by_id = {row["exercise_id"]: row for row in exact["checks"]}
    audit_by_id = {row.exercise_id: row for row in audit_capabilities(definitions)}

    rows: list[dict[str, Any]] = []
    for definition in sorted(definitions, key=lambda d: d.id):
        exact_row = exact_by_id.get(definition.id.upper())
        audit_row = audit_by_id.get(definition.id)
        if exact_row and exact_row["status"] == "VERIFIED":
            tier = "TIER_1_EXECUTABLE"
            reason = "Exact semantic binding contract is runtime-verified."
            execution_path = "EXACT_BINDING"
        elif audit_row and audit_row.status == "VERIFIED":
            tier = "TIER_1_EXECUTABLE"
            reason = audit_row.rationale
            execution_path = "VALIDATED_VERTICAL_SLICE"
        elif definition.id.startswith("STR-"):
            tier = "COMPOSITE"
            reason = "Strategic exercise is orchestrated from child capabilities."
            execution_path = "COMPOSITE_ORCHESTRATOR"
        elif audit_row and audit_row.status == "CANDIDATE":
            tier = "TIER_2_CANDIDATE"
            reason = audit_row.rationale
            execution_path = "SEMANTIC_VERIFICATION_REQUIRED"
        else:
            tier = "TIER_3_UNMAPPED"
            reason = audit_row.rationale if audit_row else "No capability audit row is available."
            execution_path = "UNMAPPED"
        rows.append({
            "exercise_id": definition.id,
            "name": definition.name,
            "domain": definition.domain,
            "tier": tier,
            "reason": reason,
            "execution_path": execution_path,
            "engine_callable": exact_row["callable"] if exact_row else None,
        })

    counts = Counter(row["tier"] for row in rows)
    by_domain: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_domain[row["domain"]][row["tier"]] += 1

    return {
        "registered_exercises": len(rows),
        "counts": dict(sorted(counts.items())),
        "coverage_pct": round((counts.get("TIER_1_EXECUTABLE", 0) / len(rows) * 100), 2) if rows else 0.0,
        "by_domain": {domain: dict(sorted(counter.items())) for domain, counter in sorted(by_domain.items())},
        "rows": rows,
    }
