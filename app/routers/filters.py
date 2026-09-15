from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import FilterSave

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("")
def list_filters(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_workspace_filters(db, user.id, workspace_id)


@router.post("")
def save_filter(body: FilterSave, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.save_workspace_filter(db, user.id, body.workspace_id, body.name, body.definition)
