from __future__ import annotations

import hashlib
import hmac
import base64
import json
import re
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from html import escape
from urllib.parse import urlsplit, urlunsplit

import httpx
from sqlalchemy.orm import Session
from .. import models
from ..config import settings

FACT = "SOURCED_FACT"
DERIVED = "DERIVED_ANALYTIC"
NARRATIVE = "AI_NARRATIVE"
DEFAULT_SECTIONS = ["daily_signals", "company_performance", "financial_intelligence"]


def _loads(value: str | None, default):
    if not value: return default
    try: return json.loads(value)
    except (TypeError, ValueError): return default


def canonicalize_url(url: str | None) -> str | None:
    if not url: return None
    try:
        p=urlsplit(url.strip())
        if p.scheme not in {"http","https"} or not p.netloc: return url.strip()
        path=re.sub(r"/+", "/", p.path).rstrip("/") or "/"
        return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, p.query, ""))
    except ValueError: return url.strip()


def source_item_hash(title: str, canonical_url: str | None, source_name: str) -> str:
    normalized_title=re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()
    base="|".join((canonical_url or "", source_name.casefold().strip(), normalized_title))
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def preference_payload(row):
    if row is None:
        return {"markets":[],"companies":[],"therapeutic_areas":[],"topics":[],"sections":DEFAULT_SECTIONS,"frequency":"daily","timezone":"UTC","email_enabled":False,"delivery_hour":8,"suppressed":False}
    return {"markets":_loads(row.markets_json,[]),"companies":_loads(row.companies_json,[]),"therapeutic_areas":_loads(row.therapeutic_areas_json,[]),"topics":_loads(row.topics_json,[]),"sections":_loads(row.sections_json,DEFAULT_SECTIONS),"frequency":row.frequency,"timezone":row.timezone,"email_enabled":row.email_enabled,"delivery_hour":row.delivery_hour,"suppressed":row.suppressed_at is not None}


def get_preferences(db:Session,user_id:int,workspace_id:int)->dict:
    return preference_payload(db.query(models.NewsletterPreference).filter_by(user_id=user_id,workspace_id=workspace_id).first())


def save_preferences(db:Session,user_id:int,workspace_id:int,payload:dict)->dict:
    row=db.query(models.NewsletterPreference).filter_by(user_id=user_id,workspace_id=workspace_id).first()
    if row is None:
        row=models.NewsletterPreference(user_id=user_id,workspace_id=workspace_id); db.add(row)
    for field in ("markets","companies","therapeutic_areas","topics","sections"):
        if field in payload: setattr(row,f"{field}_json",json.dumps(payload[field]))
    if payload.get("frequency") is not None: row.frequency=payload["frequency"]
    if payload.get("timezone") is not None:
        try: ZoneInfo(payload["timezone"])
        except ZoneInfoNotFoundError: raise ValueError("Unknown IANA timezone")
        row.timezone=payload["timezone"]
    if payload.get("email_enabled") is not None: row.email_enabled=bool(payload["email_enabled"])
    if payload.get("delivery_hour") is not None: row.delivery_hour=int(payload["delivery_hour"])
    db.commit(); db.refresh(row); return preference_payload(row)


def list_sources(db:Session,workspace_id:int)->list[dict]:
    rows=db.query(models.NewsletterSource).filter_by(workspace_id=workspace_id).order_by(models.NewsletterSource.name).all()
    return [{"id":r.id,"name":r.name,"base_url":r.base_url,"source_type":r.source_type,"region":r.region,"language":r.language,"role":r.role,"verification_priority":r.verification_priority,"active":r.active} for r in rows]


def create_source_item(db:Session,user_id:int,payload:dict)->tuple[models.NewsletterSourceItem,bool]:
    canonical=canonicalize_url(payload.get("canonical_url") or payload.get("source_url"))
    digest=source_item_hash(payload["title"],canonical,payload["source_name"])
    existing=db.query(models.NewsletterSourceItem).filter_by(workspace_id=payload["workspace_id"],content_hash=digest).first()
    if existing: return existing,False
    data=dict(payload); data["canonical_url"]=canonical; data["content_hash"]=digest
    row=models.NewsletterSourceItem(**data,created_by_id=user_id); db.add(row); db.commit(); db.refresh(row); return row,True


def verify_source_item(db:Session,item_id:int,user_id:int,status:str,evidence_level:str):
    row=db.query(models.NewsletterSourceItem).filter_by(id=item_id).first()
    if row is None: return None
    row.verification_status=status; row.evidence_level=evidence_level
    row.verified_at=datetime.now(timezone.utc) if status=="verified" else None
    row.verified_by_id=user_id if status=="verified" else None
    db.commit(); db.refresh(row); return row


def _source_item(row)->dict:
    now=datetime.now(timezone.utc); published=row.published_at; age_hours=None
    if published:
        if published.tzinfo is None: published=published.replace(tzinfo=timezone.utc)
        age_hours=round((now-published).total_seconds()/3600,1)
    return {"id":f"source-{row.id}","kind":FACT,"title":row.title,"body":row.summary or "","source":{"name":row.source_name,"url":row.canonical_url or row.source_url,"published_at":row.published_at.isoformat() if row.published_at else None,"retrieved_at":row.retrieved_at.isoformat() if row.retrieved_at else None},"freshness":{"age_hours":age_hours,"status":"fresh" if age_hours is not None and age_hours<=48 else "dated" if age_hours is not None else "unknown"},"verification":{"status":row.verification_status,"evidence_level":row.evidence_level,"verified_at":row.verified_at.isoformat() if row.verified_at else None},"market":row.market,"company":row.company,"therapeutic_area":row.therapeutic_area,"topic":row.topic}


def _matches(row,prefs)->bool:
    for key,value in (("markets",row.market),("companies",row.company),("therapeutic_areas",row.therapeutic_area),("topics",row.topic)):
        selected={str(x).casefold() for x in prefs.get(key,[]) if x}
        if selected and (not value or str(value).casefold() not in selected): return False
    return True


def build_daily_brief(db:Session,user_id:int,workspace_id:int)->dict:
    prefs=get_preferences(db,user_id,workspace_id)
    rows=db.query(models.NewsletterSourceItem).filter_by(workspace_id=workspace_id).order_by(models.NewsletterSourceItem.published_at.desc()).limit(200).all()
    matching=[r for r in rows if _matches(r,prefs)]
    # Publication output prioritizes verified evidence, but retains needs-review items for transparent in-app review.
    matching.sort(key=lambda r:(r.verification_status!="verified", -(r.published_at.timestamp() if r.published_at else 0)))
    facts=[_source_item(r) for r in matching][:12]
    verified=[x for x in facts if x["verification"]["status"]=="verified"]
    narratives=[]
    if verified:
        narratives.append({"id":"narrative-summary","kind":NARRATIVE,"title":"PharmaLens synthesis","body":f"{len(verified)} verified sourced signal(s) match your current preferences. This narrative is generated from the attributed evidence below and should be interpreted separately from source facts.","generated_at":datetime.now(timezone.utc).isoformat(),"based_on":[x["id"] for x in verified]})
    return {"title":"AI Daily Intelligence Brief","generated_at":datetime.now(timezone.utc).isoformat(),"preferences":prefs,"items":facts+narratives,"quality":{"matched_items":len(matching),"verified_items":sum(r.verification_status=="verified" for r in matching),"needs_review_items":sum(r.verification_status!="verified" for r in matching)},"legend":{FACT:"Externally sourced fact",DERIVED:"Calculated by PharmaLens",NARRATIVE:"AI-generated interpretation"}}


def build_company_intelligence(db:Session,user_id:int,workspace_id:int)->dict:
    prefs=get_preferences(db,user_id,workspace_id); selected={str(x).casefold() for x in prefs.get("companies",[]) if x}
    runs=db.query(models.ProductRun).filter_by(workspace_id=workspace_id).order_by(models.ProductRun.created_at.desc()).limit(100).all(); items=[]
    for run in runs:
        if run.product_id not in {"company","commercial_finance","company_performance","finance"}: continue
        output=_loads(run.output_definition,{}); company=str(output.get("company") or output.get("manufacturer") or "")
        if selected and company.casefold() not in selected: continue
        items.append({"id":f"run-{run.id}","kind":DERIVED,"title":f"{run.product_id.replace('_',' ').title()} analysis","body":output,"calculation":{"engine":run.product_id,"run_id":run.id},"generated_at":run.created_at.isoformat() if run.created_at else None})
    return {"title":"Company Performance & Financial Intelligence","generated_at":datetime.now(timezone.utc).isoformat(),"items":items[:12],"empty_reason":None if items else "No compatible company/finance analysis runs are available in this workspace yet."}


def render_email(brief:dict,company:dict)->str:
    def item_html(item):
        body=item.get("body",""); body=json.dumps(body,ensure_ascii=False,indent=2) if isinstance(body,dict) else body
        source=item.get("source") or {}; verification=item.get("verification") or {}
        src=f'<p><small>Source: {escape(str(source.get("name") or ""))} · Evidence: {escape(str(verification.get("evidence_level") or ""))}</small></p>' if source else ""
        return f'<article><p><strong>{escape(item.get("kind",""))}</strong></p><h3>{escape(item.get("title",""))}</h3><p>{escape(str(body))}</p>{src}</article>'
    publishable=[x for x in brief["items"] if x.get("kind")!=FACT or not x.get("verification") or (x.get("verification") or {}).get("status")=="verified"]
    return '<!doctype html><html><body><h1>PharmaLens AI</h1><h2>'+escape(brief["title"])+"</h2>"+''.join(item_html(x) for x in publishable)+"<h2>"+escape(company["title"])+"</h2>"+''.join(item_html(x) for x in company["items"])+"</body></html>"


def _token_secret() -> bytes:
    secret=settings.newsletter_token_secret.strip()
    if not secret:
        raise RuntimeError("NEWSLETTER_TOKEN_SECRET is required for email delivery")
    return secret.encode("utf-8")

def make_unsubscribe_token(user_id:int, workspace_id:int)->str:
    payload=f"{user_id}:{workspace_id}".encode("utf-8")
    sig=hmac.new(_token_secret(),payload,hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload+b"."+sig).decode("ascii").rstrip("=")

def parse_unsubscribe_token(token:str)->tuple[int,int]:
    raw=base64.urlsafe_b64decode(token+"="*(-len(token)%4))
    payload,sig=raw.rsplit(b".",1)
    expected=hmac.new(_token_secret(),payload,hashlib.sha256).digest()
    if not hmac.compare_digest(sig,expected): raise ValueError("Invalid unsubscribe token")
    user_id,workspace_id=payload.decode("utf-8").split(":",1)
    return int(user_id),int(workspace_id)

def suppress_subscription(db:Session,user_id:int,workspace_id:int)->bool:
    row=db.query(models.NewsletterPreference).filter_by(user_id=user_id,workspace_id=workspace_id).first()
    if row is None: return False
    row.email_enabled=False; row.suppressed_at=datetime.now(timezone.utc); db.commit(); return True

def _last_delivery(db:Session,user_id:int,workspace_id:int):
    return db.query(models.NewsletterDelivery).filter_by(user_id=user_id,workspace_id=workspace_id,status="sent").order_by(models.NewsletterDelivery.sent_at.desc()).first()

def delivery_is_due(pref, now:datetime|None=None, last_sent_at:datetime|None=None)->bool:
    now=now or datetime.now(timezone.utc)
    if not pref.email_enabled or pref.suppressed_at is not None: return False
    try: local=now.astimezone(ZoneInfo(pref.timezone))
    except ZoneInfoNotFoundError: return False
    if local.hour < pref.delivery_hour: return False
    if last_sent_at is None: return True
    last_local=last_sent_at.astimezone(ZoneInfo(pref.timezone))
    if pref.frequency=="daily": return last_local.date() < local.date()
    if pref.frequency=="weekly": return (local.date()-last_local.date()).days >= 7
    return False

def render_delivery_email(brief:dict,company:dict,unsubscribe_url:str)->str:
    html=render_email(brief,company)
    footer=f'<hr><p><small><a href="{escape(unsubscribe_url, quote=True)}">Unsubscribe from PharmaLens Intelligence emails</a></small></p>'
    return html.replace("</body>",footer+"</body>")

def send_newsletter_email(db:Session,user,workspace_id:int)->dict:
    pref=db.query(models.NewsletterPreference).filter_by(user_id=user.id,workspace_id=workspace_id).first()
    if pref is None or not pref.email_enabled or pref.suppressed_at is not None: return {"status":"skipped","reason":"email_not_enabled"}
    if not user.email: return {"status":"skipped","reason":"missing_recipient_email"}
    if not settings.resend_api_key or not settings.newsletter_from_email: return {"status":"disabled","reason":"email_provider_not_configured"}
    token=make_unsubscribe_token(user.id,workspace_id)
    unsubscribe_url=settings.newsletter_public_url.rstrip("/")+"/newsletter/unsubscribe?token="+token
    brief=build_daily_brief(db,user.id,workspace_id); company=build_company_intelligence(db,user.id,workspace_id)
    subject="PharmaLens AI Daily Intelligence Brief"
    html=render_delivery_email(brief,company,unsubscribe_url)
    delivery=models.NewsletterDelivery(workspace_id=workspace_id,user_id=user.id,recipient_email=user.email,subject=subject,provider="resend",status="queued")
    db.add(delivery); db.commit(); db.refresh(delivery)
    try:
        response=httpx.post("https://api.resend.com/emails",headers={"Authorization":f"Bearer {settings.resend_api_key}","Content-Type":"application/json"},json={"from":f"{settings.newsletter_from_name} <{settings.newsletter_from_email}>","to":[user.email],"subject":subject,"html":html},timeout=15.0)
        response.raise_for_status(); data=response.json(); delivery.status="sent"; delivery.provider_message_id=str(data.get("id") or ""); delivery.sent_at=datetime.now(timezone.utc); db.commit()
        return {"status":"sent","delivery_id":delivery.id,"provider_message_id":delivery.provider_message_id}
    except Exception as exc:
        delivery.status="failed"; delivery.error=str(exc)[:2000]; db.commit(); return {"status":"failed","delivery_id":delivery.id,"error":"provider_delivery_failed"}

def deliver_due_newsletters(db:Session,now:datetime|None=None)->dict:
    now=now or datetime.now(timezone.utc); sent=skipped=failed=0
    prefs=db.query(models.NewsletterPreference).filter_by(email_enabled=True).all()
    for pref in prefs:
        last=_last_delivery(db,pref.user_id,pref.workspace_id); last_sent=last.sent_at if last else None
        if not delivery_is_due(pref,now,last_sent): skipped+=1; continue
        user=db.query(models.User).filter_by(id=pref.user_id).first()
        if user is None: skipped+=1; continue
        result=send_newsletter_email(db,user,pref.workspace_id)
        if result["status"]=="sent": sent+=1
        elif result["status"]=="failed": failed+=1
        else: skipped+=1
    return {"sent":sent,"failed":failed,"skipped":skipped,"checked":len(prefs),"run_at":now.isoformat()}
