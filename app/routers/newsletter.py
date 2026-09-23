from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import NewsletterPreferencesUpdate, NewsletterSourceCreate, NewsletterSourceItemCreate, NewsletterSourceItemVerify, NewsletterSendRequest, NewsletterUnsubscribeRequest
from ..services.newsletter import build_company_intelligence, build_daily_brief, create_source_item, get_preferences, list_sources, render_email, save_preferences, verify_source_item, send_newsletter_email, parse_unsubscribe_token, suppress_subscription

router=APIRouter(prefix="/api/newsletter",tags=["newsletter"])
def _access(db,user,workspace_id):
    if not crud.is_workspace_member(db,user.id,workspace_id): raise HTTPException(403,"You do not have access to this organization")

@router.get("/preferences")
def preferences(workspace_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,workspace_id); return get_preferences(db,user.id,workspace_id)
@router.put("/preferences")
def update_preferences(body:NewsletterPreferencesUpdate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,body.workspace_id); return save_preferences(db,user.id,body.workspace_id,body.model_dump(exclude={"workspace_id"},exclude_none=True))
@router.get("/daily-brief")
def daily_brief(workspace_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,workspace_id); return build_daily_brief(db,user.id,workspace_id)
@router.get("/company-intelligence")
def company_intelligence(workspace_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,workspace_id); return build_company_intelligence(db,user.id,workspace_id)
@router.get("/email-preview")
def email_preview(workspace_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,workspace_id); brief=build_daily_brief(db,user.id,workspace_id); company=build_company_intelligence(db,user.id,workspace_id); return {"subject":"PharmaLens AI Daily Intelligence Brief","html":render_email(brief,company),"generated_at":brief["generated_at"]}

@router.get("/sources")
def sources(workspace_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,workspace_id); return {"items":list_sources(db,workspace_id)}
@router.post("/sources")
def add_source(body:NewsletterSourceCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,body.workspace_id)
    existing=db.query(models.NewsletterSource).filter_by(workspace_id=body.workspace_id,name=body.name).first()
    if existing: raise HTTPException(409,"Source already exists in this workspace")
    row=models.NewsletterSource(**body.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id":row.id,"status":"created"}
@router.post("/source-items")
def add_source_item(body:NewsletterSourceItemCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,body.workspace_id); row,created=create_source_item(db,user.id,body.model_dump()); return {"id":row.id,"status":"created" if created else "duplicate","verification_status":row.verification_status}
@router.put("/source-items/{item_id}/verification")
def verify(item_id:int,body:NewsletterSourceItemVerify,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,body.workspace_id)
    row=db.query(models.NewsletterSourceItem).filter_by(id=item_id,workspace_id=body.workspace_id).first()
    if row is None: raise HTTPException(404,"Newsletter source item not found")
    row=verify_source_item(db,item_id,user.id,body.verification_status,body.evidence_level)
    return {"id":row.id,"verification_status":row.verification_status,"evidence_level":row.evidence_level,"verified_at":row.verified_at}


@router.post("/send-now")
def send_now(body:NewsletterSendRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    _access(db,user,body.workspace_id)
    return send_newsletter_email(db,user,body.workspace_id)

@router.post("/unsubscribe")
def unsubscribe(body:NewsletterUnsubscribeRequest,db:Session=Depends(get_db)):
    try:
        user_id,workspace_id=parse_unsubscribe_token(body.token)
    except (ValueError,RuntimeError):
        raise HTTPException(400,"Invalid unsubscribe token")
    suppress_subscription(db,user_id,workspace_id)
    return {"status":"unsubscribed"}
