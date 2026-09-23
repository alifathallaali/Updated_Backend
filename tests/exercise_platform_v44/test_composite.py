from src.exercises.orchestrator import STR_004, run_composite
from src.exercises.schemas import CanonicalResult, ExerciseRun
from src.exercises.types import ExerciseStatus, QualityStatus


def child(exercise_id, value):
    return ExerciseRun(
        run_id=f"run-{exercise_id}", exercise_id=exercise_id, exercise_version="1.0",
        status=ExerciseStatus.COMPLETED, quality_status=QualityStatus.PASS,
        created_at="2026-09-21T00:00:00Z", user_id=None, organization_id=None,
        market="EG", data_snapshot="golden", engine_versions={}, parameters={},
        result=CanonicalResult(executive_summary=exercise_id, metrics=[{"id": "shared_metric", "value": value}], key_findings=[{"statement": f"finding {exercise_id}"}]),
    )


def test_str_004_completes_and_preserves_lineage():
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    assert result.status == ExerciseStatus.COMPLETED
    assert result.quality_status == QualityStatus.PASS
    assert len(result.result.lineage["child_run_ids"]) == 8
    assert result.result.lineage["synthesis_node"] == "EXE-018"


def test_str_004_detects_conflicting_metrics():
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    runs["FIN-008"] = child("FIN-008", 12)
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    assert result.status == ExerciseStatus.COMPLETED
    assert result.quality_status == QualityStatus.WARNING
    assert result.conflicts[0]["metric_id"] == "shared_metric"


def test_str_004_blocks_on_required_child_failure():
    runs = {x: child(x, 10) for x in STR_004.required_children}
    runs["MKT-003"].status = ExerciseStatus.BLOCKED
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    assert result.status == ExerciseStatus.BLOCKED
    assert result.quality_status == QualityStatus.BLOCK


def test_str_004_with_real_mkt_003_child_still_blocks_on_unbound_required_children():
    import pandas as pd
    from src.exercises.adapters import run_verified_child

    df = pd.DataFrame({"Brand Name": ["A", "A", "B"], "Sales Value": [60.0, 20.0, 20.0]})
    result = run_composite(
        STR_004,
        child_runner=lambda exercise_id: run_verified_child(exercise_id, df, data_snapshot="golden"),
    )
    assert result.child_runs["MKT-003"].status == ExerciseStatus.COMPLETED
    assert result.status == ExerciseStatus.BLOCKED
    assert result.quality_status == QualityStatus.BLOCK


def test_str_004_optional_blocked_yields_partial_not_blocked():
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    runs["MKT-011"].status = ExerciseStatus.BLOCKED
    runs["MKT-011"].quality_status = QualityStatus.BLOCK
    runs["MKT-011"].result = None
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    assert result.status == ExerciseStatus.PARTIAL
    assert result.quality_status == QualityStatus.WARNING
    assert "MKT-011" in result.result.data_quality["optional_unavailable"]
    assert result.result.lineage["synthesis_node"] == "EXE-018"


def test_str_004_required_policy_is_explicit():
    assert STR_004.required_children == ("MKT-003", "MKT-004", "MKT-010", "FIN-008")
    assert "EXE-018" not in STR_004.required_children
    assert STR_004.synthesis_node == "EXE-018"


def test_str_004_real_validated_core_returns_partial_result():
    import pandas as pd
    from src.exercises.adapters import run_verified_child

    df = pd.DataFrame({
        "Brand Name": ["A", "A", "B", "B"],
        "Manufacturer": ["M1", "M1", "M2", "M2"],
        "Therapeutic Class": ["T1", "T1", "T1", "T1"],
        "Distribution Channel": ["Retail", "Retail", "Hospital", "Hospital"],
        "Sales Value": [100.0, 110.0, 80.0, 90.0],
        "Sales Units": [10.0, 10.0, 8.0, 9.0],
        "Selling Price": [10.0, 11.0, 10.0, 10.0],
        "Year": [2026, 2026, 2026, 2026],
        "Month": [1, 2, 1, 2],
        "publication_count": [3, 4, 2, 1],
        "citation_count": [20, 30, 10, 5],
    })
    result = run_composite(
        STR_004,
        child_runner=lambda exercise_id: run_verified_child(exercise_id, df, data_snapshot="golden-str004"),
    )
    assert result.status == ExerciseStatus.PARTIAL
    assert result.quality_status == QualityStatus.WARNING
    for child_id in STR_004.required_children:
        assert result.child_runs[child_id].status == ExerciseStatus.COMPLETED
    assert result.child_runs["HCP-015"].status == ExerciseStatus.COMPLETED
    assert result.child_runs["TRD-019"].status == ExerciseStatus.COMPLETED
    assert result.child_runs["MKT-011"].status == ExerciseStatus.BLOCKED
    assert result.child_runs["SAL-012"].status == ExerciseStatus.BLOCKED
    assert result.result is not None
    assert result.result.lineage["synthesis_node"] == "EXE-018"


def test_conflict_detection_is_context_aware():
    a = child("MKT-003", 10)
    b = child("FIN-008", 12)
    a.result.metrics[0].update({"period": "2026-01", "unit": "pct"})
    b.result.metrics[0].update({"period": "2026-02", "unit": "pct"})
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    runs["MKT-003"], runs["FIN-008"] = a, b
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    assert result.conflicts == []
    assert result.quality_status == QualityStatus.PASS


def test_conflict_record_requires_review_and_preserves_context():
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    runs["MKT-003"].result.metrics[0].update({"period": "2026-Q1", "unit": "pct"})
    runs["FIN-008"].result.metrics[0].update({"period": "2026-Q1", "unit": "pct", "value": 12})
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    conflict = result.conflicts[0]
    assert conflict["type"] == "METRIC_CONFLICT"
    assert conflict["resolution"] == "REVIEW_REQUIRED"
    assert conflict["context"] == {"period": "2026-Q1", "unit": "pct"}
    assert result.result.metadata["conflicts_require_review"] is True


def test_composite_lineage_preserves_child_reproducibility_metadata():
    runs = {x: child(x, 10) for x in (*STR_004.required_children, *STR_004.optional_children)}
    runs["MKT-003"].data_snapshot = "snapshot-42"
    runs["MKT-003"].engine_versions = {"market_intelligence": "2.1"}
    result = run_composite(STR_004, child_runner=lambda x: runs[x])
    lineage = result.result.lineage
    assert lineage["child_data_snapshots"]["MKT-003"] == "snapshot-42"
    assert lineage["child_engine_versions"]["MKT-003"] == {"market_intelligence": "2.1"}
    assert lineage["child_exercise_versions"]["MKT-003"] == "1.0"
