import pandas as pd

from src.exercises.adapters import VERIFIED_BINDINGS, binding_health, run_verified_child
from src.exercises.types import ExerciseStatus, QualityStatus


def _df():
    return pd.DataFrame({
        "Year": [2025, 2025, 2025, 2025],
        "Month": [1, 1, 2, 2],
        "Selling Price": [10.0, 10.0, 12.0, 12.0],
        "Sales Units": [40.0, 60.0, 50.0, 70.0],
    })

def test_fin_008_is_verified_and_importable():
    assert "FIN-008" in VERIFIED_BINDINGS
    assert binding_health("FIN-008")["available"] is True

def test_fin_008_delegates_to_existing_finance_capability():
    run = run_verified_child("FIN-008", _df(), data_snapshot="golden-fin")
    assert run.status == ExerciseStatus.COMPLETED
    assert run.quality_status == QualityStatus.PASS
    metrics = {m["id"]: m["value"] for m in run.result.metrics}
    assert metrics["base_revenue"] == 1000.0
    assert metrics["new_revenue"] == 1440.0
    assert metrics["price_effect"] == 200.0
    assert metrics["volume_effect"] == 200.0
    assert metrics["interaction"] == 40.0
    assert metrics["total_variance"] == 440.0
    assert run.result.metadata["period_selection"] == "earliest_vs_latest_observed"

def test_fin_008_blocks_single_period():
    run = run_verified_child("FIN-008", _df().query("Month == 1"))
    assert run.status == ExerciseStatus.BLOCKED
