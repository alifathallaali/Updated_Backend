from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models


def is_workspace_member(db: Session, user_id: int, workspace_id: int) -> bool:
    return (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.user_id == user_id, models.WorkspaceMember.workspace_id == workspace_id)
        .first()
        is not None
    )


def list_user_workspaces(db: Session, user_id: int):
    rows = (
        db.query(models.Workspace, models.WorkspaceMember.role)
        .join(models.WorkspaceMember, models.WorkspaceMember.workspace_id == models.Workspace.id)
        .filter(models.WorkspaceMember.user_id == user_id)
        .order_by(desc(models.Workspace.updated_at))
        .all()
    )
    return [(workspace, role) for workspace, role in rows]


def create_workspace_for_user(db: Session, user_id: int, name: str, organization: str | None = None):
    workspace = models.Workspace(owner_id=user_id, name=name, organization=organization)
    db.add(workspace)
    db.flush()
    db.add(models.WorkspaceMember(workspace_id=workspace.id, user_id=user_id, role=models.MemberRole.owner))
    db.commit()
    db.refresh(workspace)
    return workspace


def update_workspace_for_user(db: Session, user_id: int, workspace_id: int, name: str | None, organization: str | None):
    member = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.user_id == user_id, models.WorkspaceMember.workspace_id == workspace_id)
        .first()
    )
    if not member or member.role == models.MemberRole.viewer:
        return None
    workspace = db.query(models.Workspace).get(workspace_id)
    if not workspace:
        return None
    if name is not None:
        workspace.name = name
    if organization is not None:
        workspace.organization = organization
    db.commit()
    db.refresh(workspace)
    return workspace


def update_user_profile(db: Session, user_id: int, name: str | None):
    user = db.query(models.User).get(user_id)
    if not user:
        return None
    if name is not None:
        user.name = name or None
    db.commit()
    db.refresh(user)
    return user


def list_user_notifications(db: Session, user_id: int):
    return (
        db.query(models.UserNotification)
        .filter(models.UserNotification.user_id == user_id)
        .order_by(desc(models.UserNotification.created_at))
        .limit(30)
        .all()
    )


def create_user_notification(db: Session, user_id: int, type_: str, title: str, content: str):
    notification = models.UserNotification(user_id=user_id, type=type_, title=title, content=content)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_workspace_file(db: Session, user_id: int, file_id: int):
    file = db.query(models.UploadedFile).get(file_id)
    if not file or not is_workspace_member(db, user_id, file.workspace_id):
        return None
    return file


def list_workspace_files(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.UploadedFile)
        .filter(models.UploadedFile.workspace_id == workspace_id)
        .order_by(desc(models.UploadedFile.created_at))
        .all()
    )


def register_workspace_file(db: Session, user_id: int, workspace_id: int, file_name: str, storage_key: str, mime_type: str | None):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    file = models.UploadedFile(
        workspace_id=workspace_id,
        uploaded_by_id=user_id,
        file_name=file_name,
        storage_key=storage_key,
        mime_type=mime_type,
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def list_workspace_filters(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.SavedFilter)
        .filter(models.SavedFilter.workspace_id == workspace_id)
        .order_by(desc(models.SavedFilter.updated_at))
        .all()
    )


def save_workspace_filter(db: Session, user_id: int, workspace_id: int, name: str, definition: str):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    saved = models.SavedFilter(workspace_id=workspace_id, user_id=user_id, name=name, definition=definition)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def append_copilot_message(db: Session, user_id: int, workspace_id: int, role: str, content: str):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    message = models.CopilotMessage(workspace_id=workspace_id, user_id=user_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_copilot_messages(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.CopilotMessage)
        .filter(models.CopilotMessage.workspace_id == workspace_id)
        .order_by(models.CopilotMessage.created_at)
        .limit(100)
        .all()
    )


def create_generated_report(db: Session, user_id: int, workspace_id: int, report_type: str, title: str, storage_key: str | None):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    report = models.GeneratedReport(
        workspace_id=workspace_id,
        created_by_id=user_id,
        report_type=report_type,
        title=title,
        storage_key=storage_key,
        status=models.ReportStatus.ready,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def create_product_run(db: Session, user_id: int, workspace_id: int, product_id: str, status: str, input_definition: str, output_definition: str):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    run = models.ProductRun(
        workspace_id=workspace_id,
        user_id=user_id,
        product_id=product_id,
        status=status,
        input_definition=input_definition,
        output_definition=output_definition,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_product_run(db: Session, user_id: int, run_id: int):
    run = db.query(models.ProductRun).get(run_id)
    if not run or not is_workspace_member(db, user_id, run.workspace_id):
        return None
    return run


def list_product_runs(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.ProductRun)
        .filter(models.ProductRun.workspace_id == workspace_id)
        .order_by(desc(models.ProductRun.created_at))
        .limit(100)
        .all()
    )


def list_generated_reports(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.GeneratedReport)
        .filter(models.GeneratedReport.workspace_id == workspace_id)
        .order_by(desc(models.GeneratedReport.created_at))
        .all()
    )


def get_generated_report(db: Session, user_id: int, report_id: int):
    report = db.query(models.GeneratedReport).get(report_id)
    if not report or not is_workspace_member(db, user_id, report.workspace_id):
        return None
    return report


# ---- Organization / RBAC (Part 2, 4 of the SaaS master prompt) ----

ADMIN_ROLES = {models.MemberRole.owner, models.MemberRole.admin}


def get_member_role(db: Session, user_id: int, workspace_id: int) -> models.MemberRole | None:
    member = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.user_id == user_id, models.WorkspaceMember.workspace_id == workspace_id)
        .first()
    )
    return member.role if member else None


def is_admin_member(db: Session, user_id: int, workspace_id: int) -> bool:
    return get_member_role(db, user_id, workspace_id) in ADMIN_ROLES


def list_organization_members(db: Session, workspace_id: int):
    rows = (
        db.query(models.WorkspaceMember, models.User)
        .join(models.User, models.User.id == models.WorkspaceMember.user_id)
        .filter(models.WorkspaceMember.workspace_id == workspace_id)
        .all()
    )
    return [{"userId": u.id, "name": u.name, "email": u.email, "role": m.role} for m, u in rows]


def add_organization_member(db: Session, workspace_id: int, email: str, role: models.MemberRole):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None, "User must sign up before being invited (no pending-invite email flow in this phase)."
    existing = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.user_id == user.id, models.WorkspaceMember.workspace_id == workspace_id)
        .first()
    )
    if existing:
        return None, "User is already a member of this organization."
    member = models.WorkspaceMember(workspace_id=workspace_id, user_id=user.id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member, None


def update_member_role(db: Session, workspace_id: int, target_user_id: int, role: models.MemberRole):
    member = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.user_id == target_user_id, models.WorkspaceMember.workspace_id == workspace_id)
        .first()
    )
    if not member:
        return None
    member.role = role
    db.commit()
    db.refresh(member)
    return member


# ---- Dataset Registry (Part 5, 6, 7 of the SaaS master prompt) ----

def create_dataset_with_first_version(db: Session, user_id: int, workspace_id: int, name: str, source_type: str, file_name: str, raw_storage_key: str):
    if not is_workspace_member(db, user_id, workspace_id):
        return None
    dataset = models.Dataset(workspace_id=workspace_id, owner_id=user_id, name=name, source_type=source_type)
    db.add(dataset)
    db.flush()
    version = models.DatasetVersion(
        dataset_id=dataset.id, version_number=1, raw_storage_key=raw_storage_key,
        file_name=file_name, created_by_id=user_id, status=models.DatasetStatus.uploaded,
    )
    db.add(version)
    db.flush()
    dataset.latest_version_id = version.id
    db.commit()
    db.refresh(dataset)
    db.refresh(version)
    return dataset, version


def add_dataset_version(db: Session, user_id: int, dataset_id: int, file_name: str, raw_storage_key: str):
    dataset = db.query(models.Dataset).get(dataset_id)
    if not dataset or not is_workspace_member(db, user_id, dataset.workspace_id):
        return None
    last_version = (
        db.query(models.DatasetVersion)
        .filter(models.DatasetVersion.dataset_id == dataset_id)
        .order_by(desc(models.DatasetVersion.version_number))
        .first()
    )
    next_number = (last_version.version_number + 1) if last_version else 1
    version = models.DatasetVersion(
        dataset_id=dataset_id, version_number=next_number, raw_storage_key=raw_storage_key,
        file_name=file_name, created_by_id=user_id, status=models.DatasetStatus.uploaded,
    )
    db.add(version)
    db.flush()
    dataset.latest_version_id = version.id
    dataset.status = models.DatasetStatus.uploaded
    db.commit()
    db.refresh(version)
    return version


def get_dataset(db: Session, user_id: int, dataset_id: int):
    dataset = db.query(models.Dataset).get(dataset_id)
    if not dataset or not is_workspace_member(db, user_id, dataset.workspace_id):
        return None
    return dataset


def get_dataset_version(db: Session, user_id: int, version_id: int):
    version = db.query(models.DatasetVersion).get(version_id)
    if not version:
        return None
    dataset = db.query(models.Dataset).get(version.dataset_id)
    if not dataset or not is_workspace_member(db, user_id, dataset.workspace_id):
        return None
    return version


def list_datasets(db: Session, user_id: int, workspace_id: int):
    if not is_workspace_member(db, user_id, workspace_id):
        return []
    return (
        db.query(models.Dataset)
        .filter(models.Dataset.workspace_id == workspace_id, models.Dataset.status != models.DatasetStatus.archived)
        .order_by(desc(models.Dataset.updated_at))
        .all()
    )


def list_dataset_versions(db: Session, user_id: int, dataset_id: int):
    dataset = get_dataset(db, user_id, dataset_id)
    if not dataset:
        return []
    return (
        db.query(models.DatasetVersion)
        .filter(models.DatasetVersion.dataset_id == dataset_id)
        .order_by(desc(models.DatasetVersion.version_number))
        .all()
    )


def set_version_status(db: Session, version_id: int, status: models.DatasetStatus, row_count: int | None = None, curated_storage_key: str | None = None):
    version = db.query(models.DatasetVersion).get(version_id)
    if not version:
        return None
    version.status = status
    if row_count is not None:
        version.row_count = row_count
    if curated_storage_key is not None:
        version.curated_storage_key = curated_storage_key
    dataset = db.query(models.Dataset).get(version.dataset_id)
    if dataset:
        dataset.status = status
    db.commit()
    db.refresh(version)
    return version


def save_dataset_mapping(db: Session, user_id: int, version_id: int, mapping_json: str, confidence_json: str, confirmed: bool):
    import datetime as _dt

    mapping = models.DatasetMapping(
        dataset_version_id=version_id, mapping_json=mapping_json, confidence_json=confidence_json,
        confirmed_by_id=user_id if confirmed else None,
        confirmed_at=_dt.datetime.now(_dt.timezone.utc) if confirmed else None,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def get_latest_dataset_mapping(db: Session, version_id: int):
    return (
        db.query(models.DatasetMapping)
        .filter(models.DatasetMapping.dataset_version_id == version_id)
        .order_by(desc(models.DatasetMapping.created_at))
        .first()
    )


def save_quality_report(db: Session, version_id: int, quality_score: int, critical_errors_json: str, warnings_json: str, recommendations_json: str):
    report = models.DataQualityReport(
        dataset_version_id=version_id, quality_score=quality_score, critical_errors_json=critical_errors_json,
        warnings_json=warnings_json, recommendations_json=recommendations_json,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_quality_report(db: Session, version_id: int):
    return (
        db.query(models.DataQualityReport)
        .filter(models.DataQualityReport.dataset_version_id == version_id)
        .order_by(desc(models.DataQualityReport.created_at))
        .first()
    )
