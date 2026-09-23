import pandas as pd

from src.exercises.adapters import binding_health, run_verified_child
from src.exercises.types import ExerciseStatus, QualityStatus


def test_binding_health_reports_real_import_state():
    health = binding_health("MKT-003")
    assert health["exercise_id"] == "MKT-003"
    assert health["available"] is True


def test_existing_engine_executes_real_mkt_003_adapter():
    df = pd.DataFrame({
        "Brand Name": ["A", "A", "B"],
        "Sales Value": [60.0, 20.0, 20.0],
    })
    run = run_verified_child("MKT-003", df, data_snapshot="golden")
    assert run.status == ExerciseStatus.COMPLETED
    assert run.quality_status == QualityStatus.PASS
    assert run.result is not None
    assert run.result.metrics[0]["value"] == 2
    assert round(run.result.metrics[1]["value"], 6) == 100.0


def test_missing_required_data_is_blocked_not_fabricated():
    run = run_verified_child("MKT-003", pd.DataFrame({"Brand Name": ["A"]}), data_snapshot="golden")
    assert run.status == ExerciseStatus.BLOCKED
    assert run.quality_status == QualityStatus.BLOCK
    assert "Sales Value" in run.error


def test_unregistered_child_is_blocked():
    run = run_verified_child("FIN-008", pd.DataFrame(), data_snapshot="golden")
    assert run.status == ExerciseStatus.BLOCKED
    assert run.quality_status == QualityStatus.BLOCK
