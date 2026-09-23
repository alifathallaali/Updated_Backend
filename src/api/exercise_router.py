"""Exercise Platform API router.

Mount this router in the existing FastAPI application. This module does not
create a FastAPI app and does not bypass existing authentication/RLS wiring.
"""
from __future__ import annotations
from typing import Any
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from src.exercises.adapters import run_verified_child
from src.exercises.orchestrator import STR_004, run_composite
from src.exercises.registry import registry
from src.exercises.runner import run_exercise, run_exact_bound_exercise
from src.exercises.catalog.binding_contracts import EXACT_BINDINGS
from src.exercises.binding_status import binding_status_report
from src.exercises.readiness import exercise_readiness_report
from src.exercises.production_closure import production_closure_report
from src.exercises.workspace import exercise_workspace_payload, composite_workspace_payload
from src.agents.exercise_copilot import resolve_copilot_route, run_copilot_exercise, explain_workspace

router = APIRouter(prefix="/exercises", tags=["Exercise Platform"])


class ExerciseRunRequest(BaseModel):
    # Reject caller-supplied identity/tenant fields. Authentication and tenancy
    # belong to the upstream trusted middleware/RLS context, never request JSON.
    model_config = ConfigDict(extra="forbid")
    rows: list[dict[str, Any]] = Field(min_length=1, max_length=50_000)
    parameters: dict[str, Any] = Field(default_factory=dict)
    market: str | None = None
    data_snapshot: str | None = None


class CompositeRunRequest(ExerciseRunRequest):
    pass


class CopilotRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1)
    exercise_id: str | None = None


class CopilotRunRequest(CopilotRouteRequest, ExerciseRunRequest):
    pass


def _frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        raise HTTPException(status_code=400, detail="At least one data row is required.")
    return df


@router.get("")
def list_exercises():
    return {"exercises": [d.to_dict() for d in registry.list()]}

@router.get("/bindings/status")
def get_binding_status():
    return binding_status_report()


@router.get("/readiness")
def get_exercise_readiness():
    return exercise_readiness_report()


@router.get("/production-closure")
def get_production_closure():
    return production_closure_report()


@router.post("/copilot/route")
def copilot_route(req: CopilotRouteRequest):
    return resolve_copilot_route(req.question, exercise_id=req.exercise_id).to_dict()


@router.post("/copilot/run")
def copilot_run(req: CopilotRunRequest):
    payload = run_copilot_exercise(
        req.question, req.rows, exercise_id=req.exercise_id, market=req.market,
        data_snapshot=req.data_snapshot, parameters=req.parameters,
    )
    if payload.get("workspace") is not None:
        payload["explanation"] = explain_workspace(payload["workspace"])
    return payload


@router.get("/{exercise_id}")
def get_exercise(exercise_id: str):
    try:
        return registry.get(exercise_id.upper()).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{exercise_id}/run")
def execute_exercise(exercise_id: str, req: ExerciseRunRequest):
    exercise_id = exercise_id.upper()
    if exercise_id == "STR-004":
        return execute_str_004(CompositeRunRequest(**req.model_dump()))
    try:
        registry.get(exercise_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    df = _frame(req.rows)
    if exercise_id == "SAL-008":
        run = run_exercise(df, exercise_id=exercise_id, market=req.market,
                           data_snapshot=req.data_snapshot, parameters=req.parameters)
    elif exercise_id in EXACT_BINDINGS:
        run = run_exact_bound_exercise(
            exercise_id=exercise_id, df=df, parameters=req.parameters, market=req.market,
            data_snapshot=req.data_snapshot,
        )
    else:
        # Preserve legacy verified adapters used by STR-004 compatibility nodes.
        run = run_verified_child(exercise_id, df, market=req.market,
                                 data_snapshot=req.data_snapshot)
    return exercise_workspace_payload(run)


@router.post("/STR-004/run")
def execute_str_004(req: CompositeRunRequest):
    df = _frame(req.rows)
    run = run_composite(
        STR_004,
        child_runner=lambda child_id: run_verified_child(
            child_id, df, market=req.market, data_snapshot=req.data_snapshot
        ),
    )
    return composite_workspace_payload(run)

@router.post("/{exercise_id}/export/pptx")
def export_exercise_pptx(exercise_id: str, req: ExerciseRunRequest):
    """Execute through the governed Exercise path, then render the resulting workspace."""
    from pathlib import Path
    import tempfile
    from fastapi.responses import FileResponse
    from src.exercises.export import export_workspace_pptx

    exercise_id = exercise_id.upper()
    if exercise_id == "STR-004":
        workspace = execute_str_004(CompositeRunRequest(**req.model_dump()))
    else:
        workspace = execute_exercise(exercise_id, req)
    output = Path(tempfile.gettempdir()) / f"pharmalens_{exercise_id.lower()}_{workspace['run_id']}.pptx"
    export_workspace_pptx(workspace, output)
    return FileResponse(output, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=f"{exercise_id}_{workspace['run_id']}.pptx")
