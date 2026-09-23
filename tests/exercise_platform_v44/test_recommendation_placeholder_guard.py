from src.exercises.adapters import VERIFIED_BINDINGS, run_verified_child
from src.exercises.semantic_mapping import candidates_for
from src.exercises.semantic_verification import verify_str_004
import pandas as pd


def test_placeholder_opportunity_capability_is_not_promoted():
    assert "MKT-011" not in VERIFIED_BINDINGS
    assert "SAL-012" not in VERIFIED_BINDINGS
    assert candidates_for("MKT-011")[0].status == "UNMAPPED"
    assert candidates_for("SAL-012")[0].status == "UNMAPPED"


def test_placeholder_children_fail_closed():
    df = pd.DataFrame({"Sales Value": [100.0, 120.0]})
    for exercise_id in ("MKT-011", "SAL-012"):
        run = run_verified_child(exercise_id, df)
        assert run.status.value == "BLOCKED"
        assert run.result is None


def test_semantic_verification_reports_placeholder_children_blocked():
    rows = {r.exercise_id: r for r in verify_str_004()}
    assert rows["MKT-011"].status == "BLOCKED"
    assert rows["SAL-012"].status == "BLOCKED"
    assert "pass-through placeholder" in rows["MKT-011"].reason
    assert "pass-through placeholder" in rows["SAL-012"].reason
