from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.exercise_router import router


def _client():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


def _rows():
    return [
        {"period":"2026-01-01","Sales Value":100.0,"Sales Units":10,"Brand Name":"A","Manufacturer":"M1","Therapeutic Class":"T","Distribution Channel":"Retail","Year":2026,"Month":1,"Selling Price":10.0},
        {"period":"2026-02-01","Sales Value":90.0,"Sales Units":10,"Brand Name":"A","Manufacturer":"M1","Therapeutic Class":"T","Distribution Channel":"Retail","Year":2026,"Month":2,"Selling Price":9.0},
    ]


def test_http_sal008_end_to_end_workspace_contract():
    response = _client().post("/api/v1/exercises/SAL-008/run", json={"rows": _rows(), "data_snapshot": "e2e-snap"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["contract"] == "pharmalens.exercise_workspace.v1"
    assert payload["id"] == "SAL-008"
    assert payload["status"] == "COMPLETED"
    assert payload["copilot_context"]["evidence_only"] is True


def test_http_rejects_identity_injection():
    response = _client().post(
        "/api/v1/exercises/SAL-008/run",
        json={"rows": _rows(), "organization_id": "other-tenant", "user_id": "attacker"},
    )
    assert response.status_code == 422
