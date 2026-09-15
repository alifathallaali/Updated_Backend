from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/product-runs", tags=["product-runs"])


@router.get("")
def list_runs(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_product_runs(db, user.id, workspace_id)
