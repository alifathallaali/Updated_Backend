"""Exercise-aware Copilot bridge.

This module extends the existing agent layer without replacing it.  It routes
supported natural-language questions through the governed Exercise Platform and
returns the Universal Workspace contract as the evidence boundary.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd

from src.exercises.resolver import resolve_exercise
from src.exercises.runner import run_exercise
from src.exercises.adapters import run_verified_child
from src.exercises.orchestrator import STR_004, run_composite
from src.exercises.workspace import exercise_workspace_payload, composite_workspace_payload


@dataclass(frozen=True)
class CopilotRoute:
    intent: str
    exercise_id: str | None
    status: str
    needs_data: bool = True
    clarification: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_copilot_route(question: str, *, exercise_id: str | None = None) -> CopilotRoute:
    """Resolve only governed Exercise intents; never guess unsupported routes."""
    q = (question or "").strip()
    if exercise_id:
        eid = exercise_id.upper()
        if eid == "STR-004":
            return CopilotRoute("STRATEGIZE", eid, "RESOLVED")
        try:
            definition = resolve_exercise(q or eid, exercise_id=eid)
            return CopilotRoute(definition.type.value, definition.id, "RESOLVED")
        except KeyError:
            return CopilotRoute("UNKNOWN", None, "UNRESOLVED", clarification="The requested exercise is not registered.")

    ql = q.lower()
    if any(term in ql for term in ("brand growth strategy", "growth strategy", "strategic brand review")):
        return CopilotRoute("STRATEGIZE", "STR-004", "RESOLVED")
    try:
        definition = resolve_exercise(q)
        return CopilotRoute(definition.type.value, definition.id, "RESOLVED")
    except KeyError:
        return CopilotRoute(
            "UNKNOWN", None, "CLARIFICATION_REQUIRED", needs_data=False,
            clarification="I could not map that question to a validated Exercise. Please specify the analysis you want to run."
        )


def run_copilot_exercise(
    question: str,
    rows: list[dict[str, Any]],
    *,
    exercise_id: str | None = None,
    market: str | None = None,
    data_snapshot: str | None = None,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a resolved Exercise and return only governed workspace evidence."""
    route = resolve_copilot_route(question, exercise_id=exercise_id)
    if not route.exercise_id:
        return {"route": route.to_dict(), "workspace": None}
    df = pd.DataFrame(rows)
    if df.empty:
        return {
            "route": route.to_dict(),
            "workspace": None,
            "error": "At least one data row is required to run the resolved Exercise.",
        }
    eid = route.exercise_id
    if eid == "STR-004":
        run = run_composite(
            STR_004,
            child_runner=lambda child_id: run_verified_child(
                child_id, df, market=market, data_snapshot=data_snapshot
            ),
        )
        workspace = composite_workspace_payload(run)
    elif eid == "SAL-008":
        run = run_exercise(
            df, exercise_id=eid, market=market, data_snapshot=data_snapshot,
            parameters=parameters or {},
        )
        workspace = exercise_workspace_payload(run)
    else:
        run = run_verified_child(eid, df, market=market, data_snapshot=data_snapshot)
        workspace = exercise_workspace_payload(run)
    return {"route": route.to_dict(), "workspace": workspace}


def explain_workspace(workspace: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic Copilot answer envelope from canonical evidence only."""
    context = dict(workspace.get("copilot_context") or {})
    if not context:
        return {"answer": "No validated Exercise result is available to explain.", "evidence": [], "limitations": []}
    summary = context.get("executive_summary") or "The Exercise completed without an executive summary."
    limitations = list(workspace.get("limitations") or [])
    return {
        "answer": summary,
        "exercise_id": context.get("exercise_id"),
        "run_id": context.get("run_id"),
        "quality_status": context.get("quality_status"),
        "evidence": {
            "metrics": context.get("metrics", []),
            "findings": context.get("findings", []),
            "lineage": context.get("lineage", {}),
        },
        "limitations": limitations,
        "evidence_only": True,
    }
