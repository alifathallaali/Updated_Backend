from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..ai_service import AIUnavailable, generate_ai_response
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import CopilotAppend, CopilotAsk
from ..skill_registry import read_skill, select_commercial_skills

router = APIRouter(prefix="/api/copilot", tags=["copilot"])

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
    crud.append_copilot_message(db, user.id, body.workspace_id, "user", body.message)
    selected = select_commercial_skills(body.message)
    framework = "\n\n".join(read_skill(skill) for skill in selected)
    context = body.data_context
    if framework:
        context += "\n\nCOMMERCIAL_SKILL_FRAMEWORK (guidance only, not customer evidence):\n" + framework
    try:
        result = await generate_ai_response(body.message, context, body.analysis_type, body.workspace, body.filters)
    except AIUnavailable:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable. Please try again.")
    crud.append_copilot_message(db, user.id, body.workspace_id, "assistant", result.reply)
    return {"status": "success", "content": result.reply, "reply": result.reply, "provider_used": result.provider, "fallback_used": result.fallback_used}
