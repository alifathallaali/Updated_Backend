import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import canonical_service, crud
from ..ai_service import AIUnavailable, generate_ai_response, provider_status
from ..database import get_db
from ..deps import get_current_user
from ..models import DatasetStatus, User
from ..schemas import CopilotAppend, CopilotAsk
from ..skill_registry import read_skill, select_commercial_skills
from ..engines.intent_resolver import resolve_dataset_goal
from ..engines.engine_registry import run_product_engine
from ..engines.heor_adapters.grounding import heor_grounding_requirement
from ..security import enforce_copilot_limit

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/copilot", tags=["copilot"])



@router.get("/health")
def copilot_health():
    providers = provider_status()
    return {"status": "ready" if any(item["configured"] for item in providers) else "misconfigured", "providers": providers}


@router.get("/history")
def history(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    return crud.list_copilot_messages(db, user.id, workspace_id)


@router.post("/append")
def append(body: CopilotAppend, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    return crud.append_copilot_message(db, user.id, body.workspace_id, body.role, body.content)


@router.post("/ask")
async def ask(body: CopilotAsk, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Grounded Copilot: route against governed schema, calculate first, explain second."""
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    enforce_copilot_limit(user.id)

    source = None
    rows = []
    parsed = None
    version = None
    if body.dataset_version_id is not None:
        version = crud.get_dataset_version(db, user.id, body.dataset_version_id)
    elif body.dataset_id is not None:
        dataset = crud.get_dataset(db, user.id, body.dataset_id)
        if not dataset or dataset.workspace_id != body.workspace_id:
            raise HTTPException(403, "Dataset is not in this workspace")
        if dataset.latest_version_id:
            version = crud.get_dataset_version(db, user.id, dataset.latest_version_id)
    if version is not None:
        dataset = crud.get_dataset(db, user.id, version.dataset_id)
        if not dataset or dataset.workspace_id != body.workspace_id:
            raise HTTPException(403, "Dataset version is not in this workspace")
        if getattr(version.status, "value", version.status) != DatasetStatus.ready.value:
            raise HTTPException(409, "Dataset version is not ready for Copilot analysis")
        try:
            parsed = canonical_service.load_canonical_dataset_version(version)
            source = parsed["source"]
            rows = parsed.get("rows", [])[:25000]
        except Exception as error:
            log.exception("Copilot dataset context failed workspace_id=%s", body.workspace_id)
            raise HTTPException(422, "The selected dataset could not be prepared for Copilot") from error

    crud.append_copilot_message(db, user.id, body.workspace_id, "user", body.message)
    grounding = {"status": "DATA_REQUIRED", "reason": "No governed dataset is attached.", "rawRowsSentToLLM": False}
    analytical_result = None
    run_id = None
    if parsed is not None:
        columns = list((parsed.get("schema") or {}).get("mapping", {}).values())
        if not columns and rows:
            columns = list(rows[0].keys())
        route = resolve_dataset_goal(columns, body.message, profile=parsed.get("profile") or {}, persona=body.persona)
        rec = route.get("recommendedExercise")
        grounding = {"status": "PARTIAL" if route.get("requiresUserClarification") else "ANSWERED", "route": route, "rawRowsSentToLLM": False}
        if body.auto_run and rec and rec.get("state") == "ready":
            heor_requirement = heor_grounding_requirement(rec, body.filters)
            if heor_requirement:
                grounding = {**grounding, **heor_requirement}
            else:
                analytical_result = run_product_engine(rec["exerciseId"], rows, {"workspaceId": body.workspace_id, "filters": body.filters, "datasetVersionId": version.id})
                saved = crud.create_product_run(db, user.id, body.workspace_id, rec["exerciseId"], analytical_result["status"],
                    __import__('json').dumps({"datasetVersionId": version.id, "datasetId": version.dataset_id, "filters": body.filters or {}, "rowCount": len(rows), "origin": "grounded_copilot", "question": body.message}),
                    __import__('json').dumps(analytical_result))
                run_id = saved.id if saved else None

    # Only schema/profile + deterministic analytical output are supplied to the LLM; never raw rows.
    context_parts = [body.data_context]
    if parsed is not None:
        context_parts.append(f"DATASET_SOURCE: {source}\nPROFILE: {parsed.get('profile')}\nGOVERNANCE: {parsed.get('governance')}")
    context_parts.append("GROUNDING: " + __import__('json').dumps(grounding, default=str))
    if analytical_result is not None:
        safe_result = {k:v for k,v in analytical_result.items() if k not in {"rows", "raw_rows"}}
        context_parts.append("DETERMINISTIC_ANALYSIS: " + __import__('json').dumps(safe_result, default=str)[:30000])
    selected = select_commercial_skills(body.message)
    framework = "\n\n".join(read_skill(skill) for skill in selected)
    context = "\n\n".join(part for part in context_parts if part)
    if framework:
        context += "\n\nCOMMERCIAL_SKILL_FRAMEWORK (guidance only, not customer evidence):\n" + framework
    try:
        result = await generate_ai_response(body.message, context, body.analysis_type, body.workspace or f"workspace_id={body.workspace_id}", body.filters)
    except AIUnavailable as error:
        raise HTTPException(status_code=503, detail={"message": "AI service temporarily unavailable.", "providers": error.failures}) from error
    crud.append_copilot_message(db, user.id, body.workspace_id, "assistant", result.reply)
    return {"status": "success", "content": result.reply, "reply": result.reply, "provider_used": result.provider,
            "fallback_used": result.fallback_used, "source": source, "grounding": grounding, "run_id": run_id,
            "trust": {"resultType": "ai_interpretation", "evidence": "deterministic_engine" if analytical_result else "governed_schema_only", "rawRowsSentToLLM": False}}
