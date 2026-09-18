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

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/copilot", tags=["copilot"])


@router.get("/health")
def copilot_health():
    providers = provider_status()
    return {"status": "ready" if any(item["configured"] for item in providers) else "misconfigured", "providers": providers}


@router.get("/history")
def history(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_copilot_messages(db, user.id, workspace_id)


@router.post("/append")
def append(body: CopilotAppend, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.append_copilot_message(db, user.id, body.workspace_id, body.role, body.content)


@router.post("/ask")
async def ask(body: CopilotAsk, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")

    context_parts = [body.data_context]
    source = None
    if body.dataset_version_id is not None:
        version = crud.get_dataset_version(db, user.id, body.dataset_version_id)
        if not version:
            raise HTTPException(404, "Dataset version not found or no access")
        dataset = crud.get_dataset(db, user.id, version.dataset_id)
        if not dataset or dataset.workspace_id != body.workspace_id:
            raise HTTPException(403, "Dataset version is not in this workspace")
        if getattr(version.status, "value", version.status) != DatasetStatus.ready.value:
            raise HTTPException(409, "Dataset version is not ready for Copilot analysis")
        try:
            parsed = canonical_service.load_canonical_dataset_version(version)
            source = parsed["source"]
            context_parts.append(
                f"DATASET_SOURCE: {source}\nPROFILE: {parsed['profile']}\nGOVERNANCE: {parsed['governance']}\n"
                f"SAMPLE_ROWS: {parsed['rows'][:120]}"
            )
        except Exception as error:
            log.exception("Copilot dataset context failed workspace_id=%s dataset_version_id=%s", body.workspace_id, body.dataset_version_id)
            raise HTTPException(422, "The selected dataset could not be prepared for Copilot") from error
    elif body.dataset_id is not None:
        dataset = crud.get_dataset(db, user.id, body.dataset_id)
        if not dataset or dataset.workspace_id != body.workspace_id:
            raise HTTPException(403, "Dataset is not in this workspace")
        if dataset.latest_version_id:
            version = crud.get_dataset_version(db, user.id, dataset.latest_version_id)
            if version:
                body.dataset_version_id = version.id

    crud.append_copilot_message(db, user.id, body.workspace_id, "user", body.message)
    selected = select_commercial_skills(body.message)
    framework = "\n\n".join(read_skill(skill) for skill in selected)
    context = "\n\n".join(part for part in context_parts if part)
    if framework:
        context += "\n\nCOMMERCIAL_SKILL_FRAMEWORK (guidance only, not customer evidence):\n" + framework
    try:
        result = await generate_ai_response(body.message, context, body.analysis_type, body.workspace or f"workspace_id={body.workspace_id}", body.filters)
    except AIUnavailable as error:
        log.error("Copilot unavailable workspace_id=%s dataset_version_id=%s failures=%s", body.workspace_id, body.dataset_version_id, error.failures)
        raise HTTPException(status_code=503, detail={"message": "AI service temporarily unavailable. Configure a working provider on the backend.", "providers": error.failures}) from error
    crud.append_copilot_message(db, user.id, body.workspace_id, "assistant", result.reply)
    return {"status": "success", "content": result.reply, "reply": result.reply, "provider_used": result.provider, "fallback_used": result.fallback_used, "source": source}
