from __future__ import annotations

import json
import sys
import types
from types import SimpleNamespace

# The release runner does not have the optional Supabase SDK installed. Stub only the
# SDK import so route authorization can be tested without network/storage access.
if "supabase" not in sys.modules:
    stub = types.ModuleType("supabase")
    stub.Client = object
    stub.create_client = lambda *_a, **_k: None
    sys.modules["supabase"] = stub

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud, deps, models
from app.database import Base, get_db
from app.config import Settings
from app.main import app
from app.routers import datasets, files, upload_jobs
from app.security import (
    _reset_rate_limits_for_tests,
    enforce_rate_limit,
    require_workspace_storage_key,
    safe_storage_filename,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def seed(db):
    a = models.User(supabase_uid="user-a", email="a@example.test")
    b = models.User(supabase_uid="user-b", email="b@example.test")
    db.add_all([a, b]); db.flush()
    wa = models.Workspace(owner_id=a.id, name="A")
    wb = models.Workspace(owner_id=b.id, name="B")
    db.add_all([wa, wb]); db.flush()
    db.add_all([
        models.WorkspaceMember(workspace_id=wa.id, user_id=a.id, role=models.MemberRole.owner),
        models.WorkspaceMember(workspace_id=wb.id, user_id=b.id, role=models.MemberRole.owner),
    ])
    db.commit()
    return a, b, wa, wb


def test_presign_requires_workspace_membership(db, monkeypatch):
    a, _, wa, wb = seed(db)
    monkeypatch.setattr(files, "storage_put_presigned_url", lambda key: {"key": key})
    _reset_rate_limits_for_tests()
    with pytest.raises(HTTPException) as exc:
        files.presign_upload(wb.id, "secret.xlsx", a, db)
    assert exc.value.status_code == 403
    result = files.presign_upload(wa.id, "../safe.xlsx", a, db)
    assert result["key"].startswith(f"workspaces/{wa.id}/uploads/")
    assert ".." not in result["key"]


def test_dataset_presign_and_server_upload_require_membership(db, monkeypatch):
    a, _, wa, wb = seed(db)
    monkeypatch.setattr(datasets, "storage_put_presigned_url", lambda key: {"key": key})
    _reset_rate_limits_for_tests()
    with pytest.raises(HTTPException) as exc:
        datasets.presign_dataset_upload(wb.id, "x.xlsx", a, db)
    assert exc.value.status_code == 403
    assert datasets.presign_dataset_upload(wa.id, "x.xlsx", a, db)["key"].startswith(f"workspaces/{wa.id}/raw/")


def test_storage_metadata_cannot_reference_another_workspace():
    require_workspace_storage_key(7, "workspaces/7/raw/a.xlsx")
    with pytest.raises(HTTPException) as exc:
        require_workspace_storage_key(7, "workspaces/8/raw/a.xlsx")
    assert exc.value.status_code == 403
    assert safe_storage_filename("../../evil.xlsx") == "evil.xlsx"


def test_cross_workspace_persisted_resources_are_not_readable(db):
    a, b, wa, wb = seed(db)
    f = models.UploadedFile(workspace_id=wb.id, uploaded_by_id=b.id, file_name="b.xlsx", storage_key=f"workspaces/{wb.id}/uploads/b.xlsx")
    d = models.Dataset(workspace_id=wb.id, owner_id=b.id, name="B data", source_type="upload")
    run = models.ProductRun(workspace_id=wb.id, user_id=b.id, product_id="product-01", status="success", input_definition="{}", output_definition="{}")
    report = models.GeneratedReport(workspace_id=wb.id, created_by_id=b.id, report_type="pdf", title="B report", storage_key=f"workspaces/{wb.id}/reports/b.pdf", status=models.ReportStatus.ready)
    msg = models.CopilotMessage(workspace_id=wb.id, user_id=b.id, role="user", content="private")
    db.add_all([f, d, run, report, msg]); db.commit()
    assert crud.get_workspace_file(db, a.id, f.id) is None
    assert crud.get_dataset(db, a.id, d.id) is None
    assert crud.get_product_run(db, a.id, run.id) is None
    assert crud.get_generated_report(db, a.id, report.id) is None
    assert crud.list_copilot_messages(db, a.id, wb.id) == []
    assert crud.list_workspace_files(db, a.id, wb.id) == []
    assert crud.list_product_runs(db, a.id, wb.id) == []
    assert crud.list_generated_reports(db, a.id, wb.id) == []


def test_missing_and_invalid_auth_fail_closed(db, monkeypatch):
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        assert client.get("/api/workspaces").status_code == 401
        monkeypatch.setattr(deps, "_decode_supabase_jwt", lambda _token: (_ for _ in ()).throw(HTTPException(401, "Invalid session token")))
        assert client.get("/api/workspaces", headers={"Authorization": "Bearer invalid"}).status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_valid_user_cannot_access_other_workspace_copilot_history(db, monkeypatch):
    a, _, _, wb = seed(db)
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(deps, "_decode_supabase_jwt", lambda _token: {"sub": a.supabase_uid, "email": a.email})
    try:
        response = TestClient(app).get(f"/api/copilot/history?workspace_id={wb.id}", headers={"Authorization": "Bearer valid"})
        assert response.status_code == 403
        assert "private" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_basic_rate_limiter_fails_closed():
    _reset_rate_limits_for_tests()
    enforce_rate_limit("test", 1, 2, 3600)
    enforce_rate_limit("test", 1, 2, 3600)
    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit("test", 1, 2, 3600)
    assert exc.value.status_code == 429


def test_upload_job_never_exposes_service_role(monkeypatch):
    monkeypatch.setattr(upload_jobs, "storage_put_presigned_url", lambda key, **kwargs: {
        "key": key, "token": "scoped-upload-token", "endpoint": "https://storage.example/upload", "method": "TUS"
    })
    payload = upload_jobs._build_upload_payload("workspaces/1/raw/test.xlsx")
    assert payload["token"] == "scoped-upload-token"
    assert "service_role" not in json.dumps(payload).lower()


def test_production_config_fails_closed_when_critical_values_missing():
    cfg = Settings(_env_file=None, env="production", database_url="", supabase_url="", supabase_service_role_key="", cors_origins="")
    with pytest.raises(RuntimeError) as exc:
        cfg.validate_production()
    assert "DATABASE_URL" in str(exc.value)
    assert "SUPABASE_SERVICE_ROLE_KEY" in str(exc.value)


def test_malformed_workspace_identifier_is_rejected(db, monkeypatch):
    a, _, _, _ = seed(db)
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(deps, "_decode_supabase_jwt", lambda _token: {"sub": a.supabase_uid, "email": a.email})
    try:
        response = TestClient(app).get("/api/files?workspace_id=not-an-int", headers={"Authorization": "Bearer valid"})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
