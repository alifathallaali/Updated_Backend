import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..reports.pdf_report import build_decision_brief_pdf
from ..reports.pptx_report import build_decision_brief_pptx
from ..reports.export_parity import prepare_export_output
from ..schemas import ReportFromRun, ReportSelectionFromRun
from ..storage import storage_get_signed_url, storage_put

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _load_run_output(db: Session, user: User, workspace_id: int, run_id: int):
    if not crud.is_workspace_member(db, user.id, workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    run = crud.get_product_run(db, user.id, run_id)
    if not run or run.workspace_id != workspace_id:
        raise HTTPException(404, "Product run not found in this workspace")
    try:
        output = json.loads(run.output_definition)
    except json.JSONDecodeError:
        raise HTTPException(500, "Saved run output is not readable")
    return run, output


def _selected_output(output: dict, body: ReportSelectionFromRun) -> dict:
    selected = set(body.selected_chart_ids or [])
    filtered = dict(output)
    if selected:
        filtered["visualizations"] = [
            chart for chart in (output.get("visualizations") or [])
            if chart.get("chartId") in selected
        ]
    if not body.include_metrics:
        filtered["metrics"] = {}
    if not body.include_evidence:
        filtered["evidence"] = []
    return filtered


@router.get("")
def list_reports(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_generated_reports(db, user.id, workspace_id)


@router.get("/{report_id}/download")
def download(report_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = crud.get_generated_report(db, user.id, report_id)
    if not report or not report.storage_key:
        raise HTTPException(404, "Report not found")
    return RedirectResponse(storage_get_signed_url(report.storage_key), status_code=307)


@router.post("/pdf-from-run")
def create_pdf_from_run(body: ReportSelectionFromRun, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run, output = _load_run_output(db, user, body.workspace_id, body.run_id)
    output = prepare_export_output(_selected_output(output, body))
    pdf_bytes = build_decision_brief_pdf(run.product_id, run.status, output)
    artifact = storage_put(f"workspaces/{body.workspace_id}/reports/{run.product_id}-decision-brief.pdf", pdf_bytes, "application/pdf")
    report = crud.create_generated_report(db, user.id, body.workspace_id, "decision-brief-pdf", f"{run.product_id} Decision Brief PDF", artifact["key"])
    if not report:
        raise HTTPException(500, "PDF report could not be saved")
    return {"id": report.id, "title": report.title, "downloadPath": f"/api/reports/{report.id}/download"}


@router.post("/pptx-from-run")
def create_pptx_from_run(body: ReportSelectionFromRun, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run, output = _load_run_output(db, user, body.workspace_id, body.run_id)
    output = prepare_export_output(_selected_output(output, body))
    pptx_bytes = build_decision_brief_pptx(run.product_id, run.status, output)
    artifact = storage_put(
        f"workspaces/{body.workspace_id}/reports/{run.product_id}-decision-brief.pptx", pptx_bytes,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    report = crud.create_generated_report(db, user.id, body.workspace_id, "decision-brief-pptx", f"{run.product_id} Decision Brief PPTX", artifact["key"])
    if not report:
        raise HTTPException(500, "PPTX report could not be saved")
    return {"id": report.id, "title": report.title, "downloadPath": f"/api/reports/{report.id}/download"}


@router.post("/from-run")
def create_from_run(body: ReportFromRun, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run, output = _load_run_output(db, user, body.workspace_id, body.run_id)
    DASH = "\u2014"

    metrics = "\n".join(f"- {k.replace('_', ' ')}: {v if v is not None else DASH}" for k, v in (output.get("metrics") or {}).items())
    evidence = "\n".join(f"- {i['field']}: {i.get('value') if i.get('value') is not None else DASH} ({i['source']})" for i in (output.get("evidence") or []))
    confidence = output.get("confidence") or {}
    brief = f"""# PharmaLens AI Decision Brief

Made by PharmaLens AI

## Workflow

- Product: {run.product_id}
- Status: {run.status}
- Generated: {datetime.now(timezone.utc).isoformat()}

## Decision summary

{output.get('summary') or 'Saved product decision output.'}

## Metrics

{metrics or '- No metrics recorded'}

## Evidence

{evidence or '- No evidence references recorded'}

## Confidence

{confidence.get('level', 'unknown')} ({round((confidence.get('score') or 0) * 100)}%)

> Review the evidence and confidence before making business decisions.
"""
    artifact = storage_put(f"workspaces/{body.workspace_id}/reports/{run.product_id}-decision-brief.md", brief.encode("utf-8"), "text/markdown; charset=utf-8")
    report = crud.create_generated_report(db, user.id, body.workspace_id, "decision-brief", f"{run.product_id} Decision Brief", artifact["key"])
    if not report:
        raise HTTPException(500, "Report could not be saved")
    return {"id": report.id, "title": report.title, "downloadPath": f"/api/reports/{report.id}/download"}
