from __future__ import annotations

from collections import Counter
from typing import Any

from .binding_status import binding_status_report
from .readiness import exercise_readiness_report
from .catalog.canonical_audit import audit_canonical_catalog
from .catalog import CANONICAL_EXERCISE_DEFINITIONS
from .registry import registry
from .definitions_str004 import STR_004_CHILD_DEFINITIONS


def production_closure_report() -> dict[str, Any]:
    """Single conservative release-gate summary for the Exercise Platform.

    Runtime compatibility nodes are deliberately separated from the canonical
    catalog. The historical target of 250 is not treated as source material.
    """
    definitions = registry.list()
    readiness = exercise_readiness_report()
    bindings = binding_status_report()
    canonical = list(CANONICAL_EXERCISE_DEFINITIONS)
    audit = audit_canonical_catalog(canonical, definitions, STR_004_CHILD_DEFINITIONS)

    blockers: list[str] = []
    if bindings["blocked_exact_bindings"]:
        blockers.append("One or more exact semantic bindings are blocked at runtime.")
    if audit.duplicate_canonical_ids:
        blockers.append("Duplicate exercise IDs exist in the canonical catalog.")
    if audit.target_gap:
        blockers.append(
            "The historical 250-exercise target has an unresolved canonical gap; do not fabricate definitions to close it."
        )
    if audit.legacy_only_ids:
        blockers.append("Legacy compatibility IDs remain outside the canonical catalog and must stay explicitly labeled.")
    if audit.semantic_collisions:
        blockers.append("Legacy/canonical semantic collisions remain compatibility concerns and must not overwrite canonical definitions.")

    counts = Counter(row["tier"] for row in readiness["rows"])
    return {
        "release_gate": "READY_WITH_DOCUMENTED_GAPS" if not bindings["blocked_exact_bindings"] else "BLOCKED",
        "registered_runtime_definitions": readiness["registered_exercises"],
        "canonical_definitions": audit.canonical_count,
        "historical_target": 250,
        "canonical_target_gap": audit.target_gap,
        "legacy_only_ids": list(audit.legacy_only_ids),
        "semantic_collision_ids": [row.exercise_id for row in audit.semantic_collisions],
        "tier_counts": dict(sorted(counts.items())),
        "tier1_coverage_pct": readiness["coverage_pct"],
        "exact_bindings": bindings["exact_binding_contracts"],
        "verified_exact_bindings": bindings["verified_exact_bindings"],
        "blocked_exact_bindings": bindings["blocked_exact_bindings"],
        "blockers_or_gaps": blockers,
        "principles": {
            "new_duplicate_analytics_engines": 0,
            "missing_is_zero": False,
            "unverified_binding_is_executable": False,
            "historical_target_implies_definition": False,
        },
    }
