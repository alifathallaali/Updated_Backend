from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import canonical_service, crud
from ..database import get_db
from ..deps import get_current_user
from ..engines.market_insights import build_market_insights
from ..models import User
from ..schemas import FileRegister
from ..storage import storage_put_presigned_url

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("")
def list_files(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_workspace_files(db, user.id, workspace_id)


@router.post("/presign")
def presign_upload(workspace_id: int, file_name: str, user: User = Depends(get_current_user)):
    """Returns a direct-to-R2 presigned PUT URL for large files (matches the
    Upload 500MB Excel -> Worker background-processing flow in the architecture doc)."""
    return storage_put_presigned_url(f"workspaces/{workspace_id}/uploads/{file_name}")


@router.post("")
def register_file(body: FileRegister, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    file = crud.register_workspace_file(db, user.id, body.workspace_id, body.file_name, body.storage_key, body.mime_type)
    if not file:
        raise HTTPException(403, "You do not have access to this workspace")
    return file


@router.get("/{file_id}/market-insights")
def market_insights(file_id: int, workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    file = crud.get_workspace_file(db, user.id, file_id)
    if not file or file.workspace_id != workspace_id:
        raise HTTPException(404, "File not found in this workspace")
    try:
        parsed = canonical_service.load_canonical_file(file)
    except ValueError as error:
        raise HTTPException(400, str(error))
    return build_market_insights(
        parsed["rows"],
        {
            "fileId": file.id, "fileName": file.file_name, "rawRowCount": parsed["rawRowCount"],
            "governedRowCount": len(parsed["rows"]), "validationWarnings": parsed["validation"]["warnings"],
        },
    )
