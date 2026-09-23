from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    organization: str | None = Field(default=None, max_length=200)


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    organization: str | None = Field(default=None, max_length=200)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)


class NotificationCreate(BaseModel):
    type: Literal["report_ready", "workspace_invite", "access_alert"]
    title: str = Field(max_length=255)
    content: str


class FileRegister(BaseModel):
    workspace_id: int
    file_name: str = Field(max_length=255)
    storage_key: str = Field(max_length=512)
    mime_type: str | None = Field(default=None, max_length=120)


class FilterSave(BaseModel):
    workspace_id: int
    name: str = Field(max_length=160)
    definition: str


class ProductRunRequest(BaseModel):
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-9])$")
    workspace_id: int
    rows: list[dict[str, Any]] = Field(max_length=25000)
    filters: dict[str, Any] | None = None


class ProductRunFromFileRequest(BaseModel):
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-9])$")
    workspace_id: int
    file_id: int
    filters: dict[str, Any] | None = None


class ProductRunFromDatasetVersionRequest(BaseModel):
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-9])$")
    workspace_id: int
    dataset_version_id: int
    filters: dict[str, Any] | None = None


class CopilotAsk(BaseModel):
    workspace_id: int
    message: str = Field(min_length=1, max_length=4000)
    dataset_id: int | None = None
    dataset_version_id: int | None = None
    data_context: str = Field(default="", max_length=20000)
    analysis_type: str | None = Field(default=None, max_length=120)
    workspace: str | None = Field(default=None, max_length=160)
    filters: dict[str, Any] | None = None
    persona: str | None = Field(default=None, max_length=80)
    auto_run: bool = True


class CopilotAppend(BaseModel):
    workspace_id: int
    role: Literal["user", "assistant"]
    content: str


class ProductRunRefreshRequest(BaseModel):
    workspace_id: int
    dataset_version_id: int | None = None


class ReportFromRun(BaseModel):
    workspace_id: int
    run_id: int


class ReportSelectionFromRun(ReportFromRun):
    selected_chart_ids: list[str] = Field(default_factory=list, max_length=20)
    include_metrics: bool = True
    include_evidence: bool = True


class MemberInvite(BaseModel):
    email: str
    role: Literal["admin", "manager", "analyst", "sales_user", "editor", "viewer"]


class MemberRoleUpdate(BaseModel):
    role: Literal["admin", "manager", "analyst", "sales_user", "editor", "viewer"]


class DatasetCreate(BaseModel):
    workspace_id: int
    name: str = Field(max_length=200)
    source_type: str = Field(default="user_upload", max_length=60)
    file_name: str = Field(max_length=255)
    storage_key: str = Field(max_length=512)


class DatasetVersionCreate(BaseModel):
    file_name: str = Field(max_length=255)
    storage_key: str = Field(max_length=512)


class MappingConfirm(BaseModel):
    mapping: dict[str, str]
    confidence: dict[str, float] = Field(default_factory=dict)


class AchievementAnalyze(BaseModel):
    workspace_id: int
    dataset_version_id: int
    target_field: str | None = None
    actual_field: str | None = None
    period_field: str | None = None


class UploadSessionRequest(BaseModel):
    workspace_id: int
    file_name: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(gt=0)
    mime_type: str | None = Field(default=None, max_length=120)
    idempotency_key: str = Field(min_length=8, max_length=160)


class UploadCompleteRequest(BaseModel):
    workspace_id: int
    job_id: int
    dataset_name: str | None = Field(default=None, max_length=200)
    source_type: str = Field(default="user_upload", max_length=60)


class DatasetGoalResolveRequest(BaseModel):
    workspace_id: int
    dataset_version_id: int
    goal: str = Field(min_length=1, max_length=2000)
    persona: str | None = Field(default=None, max_length=80)



class NewsletterPreferencesUpdate(BaseModel):
    workspace_id: int
    markets: list[str] | None = None
    companies: list[str] | None = None
    therapeutic_areas: list[str] | None = None
    topics: list[str] | None = None
    sections: list[str] | None = None
    frequency: str | None = None
    timezone: str | None = None
    email_enabled: bool | None = None
    delivery_hour: int | None = Field(default=None, ge=0, le=23)

class NewsletterSourceCreate(BaseModel):
    workspace_id: int
    name: str = Field(min_length=1, max_length=255)
    base_url: str | None = Field(default=None, max_length=1200)
    source_type: str = "news"
    region: str | None = None
    language: str | None = None
    role: str = "discovery"
    verification_priority: str = "medium"
    active: bool = True

class NewsletterSourceItemVerify(BaseModel):
    workspace_id: int
    verification_status: Literal["unverified", "verified", "rejected", "needs_review"]
    evidence_level: Literal["E0", "E1", "E2", "E3"]

class NewsletterSourceItemCreate(BaseModel):
    workspace_id: int
    title: str
    summary: str | None = None
    source_name: str
    source_url: str | None = None
    market: str | None = None
    company: str | None = None
    therapeutic_area: str | None = None
    topic: str | None = None
    published_at: datetime | None = None
    canonical_url: str | None = None
    verification_status: Literal["unverified", "verified", "needs_review"] = "unverified"
    evidence_level: Literal["E0", "E1", "E2", "E3"] = "E0"


class NewsletterSendRequest(BaseModel):
    workspace_id: int

class NewsletterUnsubscribeRequest(BaseModel):
    token: str = Field(min_length=20, max_length=2000)
