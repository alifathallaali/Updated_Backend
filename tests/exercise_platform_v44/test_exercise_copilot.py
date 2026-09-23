from src.agents.exercise_copilot import resolve_copilot_route, run_copilot_exercise, explain_workspace


def rows():
    return [
        {"Month":"2026-01","Year":2026,"Sales Value":100.0},
        {"Month":"2026-02","Year":2026,"Sales Value":110.0},
        {"Month":"2026-03","Year":2026,"Sales Value":105.0},
        {"Month":"2026-04","Year":2026,"Sales Value":90.0},
    ]


def test_routes_sales_decline_to_sal008():
    route = resolve_copilot_route("Why did sales decline?")
    assert route.exercise_id == "SAL-008"
    assert route.status == "RESOLVED"


def test_routes_brand_growth_strategy_to_str004():
    route = resolve_copilot_route("Run a brand growth strategy")
    assert route.exercise_id == "STR-004"


def test_unknown_intent_requires_clarification_not_guessing():
    route = resolve_copilot_route("Tell me something interesting")
    assert route.exercise_id is None
    assert route.status == "CLARIFICATION_REQUIRED"


def test_copilot_executes_sal008_through_workspace_boundary():
    payload = run_copilot_exercise("Why did sales decline?", rows())
    ws = payload["workspace"]
    assert ws["contract"] == "pharmalens.exercise_workspace.v1"
    assert ws["id"] == "SAL-008"
    assert ws["copilot_context"]["evidence_only"] is True
    assert "metadata" not in ws["copilot_context"]


def test_explanation_uses_canonical_evidence_only():
    payload = run_copilot_exercise("sales decline", rows())
    answer = explain_workspace(payload["workspace"])
    assert answer["evidence_only"] is True
    assert answer["exercise_id"] == "SAL-008"
    assert answer["evidence"]["metrics"]
    assert answer["evidence"]["lineage"]
