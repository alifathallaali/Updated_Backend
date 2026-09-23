from fastapi import HTTPException
from src.api.exercise_router import ExerciseRunRequest, CompositeRunRequest, CopilotRouteRequest, CopilotRunRequest, execute_exercise, execute_str_004, get_exercise, copilot_route, copilot_run


def _rows():
    return [
        {"period":"2026-01-01","Sales Value":100.0,"Sales Units":10,"Brand Name":"A","Manufacturer":"M1","Therapeutic Class":"T","Distribution Channel":"Retail","Year":2026,"Month":1,"Selling Price":10.0},
        {"period":"2026-02-01","Sales Value":90.0,"Sales Units":10,"Brand Name":"A","Manufacturer":"M1","Therapeutic Class":"T","Distribution Channel":"Retail","Year":2026,"Month":2,"Selling Price":9.0},
    ]


def test_sal008_api_returns_workspace_contract():
    payload=execute_exercise("SAL-008", ExerciseRunRequest(rows=_rows(), data_snapshot="snap-api"))
    assert payload["contract"] == "pharmalens.exercise_workspace.v1"
    assert payload["id"] == "SAL-008"
    assert payload["status"] == "COMPLETED"
    assert payload["copilot_context"]["evidence_only"] is True


def test_str004_api_returns_partial_workspace_not_raw_engine_output():
    payload=execute_str_004(CompositeRunRequest(rows=_rows(), data_snapshot="snap-composite"))
    assert payload["kind"] == "composite"
    assert payload["id"] == "STR-004"
    assert payload["status"] == "PARTIAL"
    assert "sections" in payload and "copilot_context" in payload
    assert "raw" not in payload


def test_unknown_exercise_is_404():
    try:
        get_exercise("DOES-NOT-EXIST")
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected HTTPException")



def test_copilot_route_endpoint():
    payload = copilot_route(CopilotRouteRequest(question="Why did sales decline?"))
    assert payload["exercise_id"] == "SAL-008"


def test_copilot_run_returns_workspace_and_evidence_explanation():
    payload = copilot_run(CopilotRunRequest(
        question="Why did sales decline?",
        rows=[
            {"Month": "2026-01", "Sales Value": 100},
            {"Month": "2026-04", "Sales Value": 90},
        ],
        data_snapshot="copilot-api-test",
    ))
    assert payload["workspace"]["id"] == "SAL-008"
    assert payload["explanation"]["evidence_only"] is True
