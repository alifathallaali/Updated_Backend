import pytest
from pydantic import ValidationError
from src.api.exercise_router import ExerciseRunRequest, CopilotRouteRequest


def test_client_cannot_inject_user_or_organization_identity():
    with pytest.raises(ValidationError):
        ExerciseRunRequest(
            rows=[{"period": "2026-01", "Sales Value": 1}],
            user_id="attacker",
            organization_id="other-tenant",
        )


def test_copilot_route_rejects_unknown_security_fields():
    with pytest.raises(ValidationError):
        CopilotRouteRequest(question="analyze sales", organization_id="other-tenant")


def test_run_payload_has_bounded_row_count():
    with pytest.raises(ValidationError):
        ExerciseRunRequest(rows=[{"Sales Value": 1}] * 50_001)
