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
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-4])$")
    workspace_id: int
    rows: list[dict[str, Any]] = Field(max_length=25000)
    filters: dict[str, Any] | None = None


class ProductRunFromFileRequest(BaseModel):
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-4])$")
    workspace_id: int
    file_id: int
    filters: dict[str, Any] | None = None


class ProductRunFromDatasetVersionRequest(BaseModel):
    product_id: str = Field(pattern=r"^product-(0[1-9]|1[0-4])$")
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


class CopilotAppend(BaseModel):
    workspace_id: int
    role: Literal["user", "assistant"]
    content: str


class ReportFromRun(BaseModel):
    workspace_id: int
    run_id: int


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
