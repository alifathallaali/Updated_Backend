import enum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class MemberRole(str, enum.Enum):
    """Organization roles (a Workspace *is* the Organization/tenant boundary in this
    codebase — see Part 2 of the SaaS master prompt). 'owner'/'editor'/'viewer' are the
    original Phase-1 roles, kept for backward compatibility; 'admin'/'manager'/'analyst'/
    'sales_user' are the roles requested by the V2 upgrade. owner and admin are equivalent
    in permission checks (see is_admin_role in crud.py)."""

    owner = "owner"
    editor = "editor"
    viewer = "viewer"
    admin = "admin"
    manager = "manager"
    analyst = "analyst"
    sales_user = "sales_user"


class DatasetStatus(str, enum.Enum):
    uploaded = "uploaded"
    validating = "validating"
    mapping = "mapping"
    processing = "processing"
    ready = "ready"
    failed = "failed"
    archived = "archived"


class FileStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class ReportStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class RunStatus(str, enum.Enum):
    success = "success"
    partial = "partial"
    error = "error"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class NotificationType(str, enum.Enum):
    report_ready = "report_ready"
    workspace_invite = "workspace_invite"
    access_alert = "access_alert"


class User(Base):
    """Core user table. supabase_uid replaces the old Manus OAuth openId."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supabase_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    login_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_signed_in: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Workspace(Base):
    """Maps to "Organization" in the PharmaLens architecture doc."""

    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole, name="member_role"), default=MemberRole.viewer, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus, name="file_status"), default=FileStatus.uploaded, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SavedFilter(Base):
    __tablename__ = "saved_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class CopilotMessage(Base):
    __tablename__ = "copilot_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus, name="report_status"), default=ReportStatus.queued, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProductRun(Base):
    __tablename__ = "product_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus, name="run_status"), default=RunStatus.success, nullable=False)
    input_definition: Mapped[str] = mapped_column(Text, nullable=False)
    output_definition: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Dataset(Base):
    """Dataset Registry entry (Part 6 / Part 5 of the SaaS master prompts).
    A Dataset is the durable, versioned identity of 'this file the org keeps
    re-uploading' (e.g. 'IQVIA Sales — Egypt'); each upload becomes a DatasetVersion."""

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False, default="user_upload")
    dataset_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    status: Mapped[DatasetStatus] = mapped_column(Enum(DatasetStatus, name="dataset_status"), default=DatasetStatus.uploaded, nullable=False)
    latest_version_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class DatasetVersion(Base):
    """One processed snapshot of a Dataset (v1, v2, ...). raw_storage_key points at the
    original file in R2; curated_storage_key points at the governed Parquet output."""

    __tablename__ = "dataset_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    curated_storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[DatasetStatus] = mapped_column(Enum(DatasetStatus, name="dataset_version_status"), default=DatasetStatus.uploaded, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UploadJob(Base):
    __tablename__ = "upload_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dataset_version_id: Mapped[int | None] = mapped_column(ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    stage: Mapped[str] = mapped_column(String(64), nullable=False, default="created")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_requested: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class DatasetMapping(Base):
    """Confirmed column mapping for a dataset version, reusable on future uploads
    from the same source (Part 7: 'Store the mapping as metadata so it can be
    reused for future files from the same source')."""

    __tablename__ = "dataset_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    mapping_json: Mapped[str] = mapped_column(Text, nullable=False)  # {"canonical_field": "source_column"}
    confidence_json: Mapped[str] = mapped_column(Text, nullable=False)  # {"canonical_field": 0.0-1.0}
    confirmed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DataQualityReport(Base):
    """Data Quality Engine output for a dataset version (Part 8 / Part 19)."""

    __tablename__ = "data_quality_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    quality_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    critical_errors_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserNotification(Base):
    __tablename__ = "user_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name="notification_type"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
