from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import User
from ..skill_registry import catalog

router = APIRouter(prefix="/api/skills", tags=["skills"])

@router.get("/catalog")
def get_catalog(user: User = Depends(get_current_user)):
    # Metadata only; skill source documents remain an internal backend concern.
    return catalog()
