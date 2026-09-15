from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import NotificationCreate, ProfileUpdate

router = APIRouter(tags=["profile"])


@router.patch("/api/profile")
def update_profile(body: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated = crud.update_user_profile(db, user.id, body.name)
    return {"id": updated.id, "name": updated.name, "email": updated.email}


@router.get("/api/notifications")
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_user_notifications(db, user.id)


@router.post("/api/notifications")
def create_notification(body: NotificationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_user_notification(db, user.id, body.type, body.title, body.content)
