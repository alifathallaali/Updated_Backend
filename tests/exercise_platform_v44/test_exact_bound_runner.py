import pandas as pd
from src.exercises.runner import run_exact_bound_exercise
from src.exercises.types import ExerciseStatus, QualityStatus


def test_shared_runner_executes_verified_target_binding():
    df = pd.DataFrame({"Year": [2025, 2025], "Sales Units": [10, 20], "Sales Value": [100, 200]})
    run = run_exact_bound_exercise(exercise_id="TGT-001", df=df, parameters={"base_year": 2025}, data_snapshot="test-snapshot")
    assert run.status == ExerciseStatus.COMPLETED
    assert run.quality_status == QualityStatus.PASS
    assert run.result.lineage["data_snapshot"] == "test-snapshot"


def test_shared_runner_blocks_missing_parameters():
    run = run_exact_bound_exercise(exercise_id="FIN-014", parameters={"foreign_sales": 100})
    assert run.status == ExerciseStatus.BLOCKED
    assert "Missing execution parameters" in run.error
