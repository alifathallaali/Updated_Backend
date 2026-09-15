from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import MemberRole, User
from ..schemas import MemberInvite, MemberRoleUpdate, WorkspaceUpdate, WorkspaceCreate

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])
# NOTE: a "Workspace" here *is* the "Organization" of the SaaS master prompt — see
# Part 2/4. Kept as "workspace" in the URL/table names to stay backward-compatible
# with the Phase-1 API that already ships.


@router.get("")
def list_workspaces(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = crud.list_user_workspaces(db, user.id)
    return [{"id": w.id, "name": w.name, "organization": w.organization, "role": role} for w, role in rows]


@router.post("")
def create_workspace(body: WorkspaceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workspace = crud.create_workspace_for_user(db, user.id, body.name, body.organization)
    return {"id": workspace.id, "name": workspace.name, "organization": workspace.organization}


@router.patch("/{workspace_id}")
def update_workspace(workspace_id: int, body: WorkspaceUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workspace = crud.update_workspace_for_user(db, user.id, workspace_id, body.name, body.organization)
    if not workspace:
        return {"error": "Not found or insufficient permission"}
    return {"id": workspace.id, "name": workspace.name, "organization": workspace.organization}


# ---- Member management / RBAC (Part 3-4 of the SaaS master prompt) ----

@router.get("/{workspace_id}/members")
def list_members(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, workspace_id):
        raise HTTPException(403, "You do not have access to this organization")
    return crud.list_organization_members(db, workspace_id)


@router.post("/{workspace_id}/members")
def invite_member(workspace_id: int, body: MemberInvite, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Adds an existing PharmaLens user to the organization. A pending-invite email
    flow for users who haven't signed up yet is out of scope for this phase."""
    if not crud.is_admin_member(db, user.id, workspace_id):
        raise HTTPException(403, "Only an organization Admin can invite members")
    member, error = crud.add_organization_member(db, workspace_id, body.email, MemberRole(body.role))
    if error:
        raise HTTPException(400, error)
    return {"userId": member.user_id, "role": member.role}


@router.patch("/{workspace_id}/members/{target_user_id}")
def update_member(workspace_id: int, target_user_id: int, body: MemberRoleUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_admin_member(db, user.id, workspace_id):
        raise HTTPException(403, "Only an organization Admin can change roles")
    member = crud.update_member_role(db, workspace_id, target_user_id, MemberRole(body.role))
    if not member:
        raise HTTPException(404, "Member not found")
    return {"userId": member.user_id, "role": member.role}
