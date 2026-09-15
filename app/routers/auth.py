from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """Supabase Auth issues and refreshes the session on the frontend; this just
    echoes back the locally-synced profile row for the signed-in user."""
    return {
        "id": user.id,
        "supabaseUid": user.supabase_uid,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }
