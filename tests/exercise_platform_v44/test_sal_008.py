import pandas as pd
from src.exercises.registry import registry
from src.exercises.runner import run_exercise
from src.exercises.resolver import resolve_exercise
from src.exercises.types import ExerciseStatus, QualityStatus
from src.exercises.visualization import resolve_visualizations

def test_registry_contains_sal_008():
    assert registry.get("SAL-008").version == "1.0"

def test_resolver_sal_008():
    assert resolve_exercise("analyze sales growth trend").id == "SAL-008"

def test_sal_008_golden_dataset():
    df = pd.DataFrame({"Month": ["2026-01", "2026-02", "2026-03", "2026-04"], "Sales Value": [100, 110, 105, 90]})
    run = run_exercise(df, data_snapshot="golden-sal-008-v1")
    assert run.status == ExerciseStatus.COMPLETED
    assert run.quality_status == QualityStatus.PASS
    metric = next(x for x in run.result.metrics if x["id"] == "sales_growth_pct")
    assert metric["value"] == -10.0
    assert run.result.lineage["data_snapshot"] == "golden-sal-008-v1"

def test_sal_008_insufficient_data_blocks():
    df = pd.DataFrame({"Month": ["2026-01"], "Sales Value": [100]})
    run = run_exercise(df)
    assert run.status == ExerciseStatus.FAILED
    assert run.quality_status == QualityStatus.BLOCK

def test_sal_008_visualization():
    df = pd.DataFrame({"Month": ["2026-01", "2026-04"], "Sales Value": [100, 90]})
    run = run_exercise(df)
    specs = resolve_visualizations("SAL-008", run.result)
    assert specs[0]["chart_id"] == "SAL-008-trend"
    assert specs[0]["chart_type"] == "line"
