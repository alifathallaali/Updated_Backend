import pandas as pd
from src.exercises.adapters import binding_health, run_verified_child
from src.exercises.types import ExerciseStatus, QualityStatus


def _hcp_df():
    return pd.DataFrame({
        "hcp": ["A", "B", "C"],
        "publication_count": [10, 5, 1],
        "citation_count": [100, 30, 2],
        "clinical_trial_count": [3, 1, 0],
        "institutional_reach": [8, 5, 2],
        "conference_activity": [6, 3, 1],
        "digital_scientific_activity": [4, 2, 0],
    })


def test_hcp_015_binding_is_importable():
    health = binding_health("HCP-015")
    assert health["available"] is True
    assert health["capability"] == "medical_affairs.score_kols"


def test_hcp_015_executes_existing_engine_and_marks_modeled_score():
    run = run_verified_child("HCP-015", _hcp_df(), data_snapshot="hcp-golden")
    assert run.status == ExerciseStatus.COMPLETED
    assert run.quality_status == QualityStatus.PASS
    assert run.result is not None
    metrics = {m["id"]: m for m in run.result.metrics}
    assert metrics["kol_candidate_count"]["value"] == 3
    assert metrics["max_kol_influence_score"]["evidence_type"] == "MODELED"
    assert run.result.lineage["capability"] == "medical_affairs.score_kols"


def test_hcp_015_missing_required_input_blocks():
    run = run_verified_child("HCP-015", pd.DataFrame({"publication_count": [1]}))
    assert run.status == ExerciseStatus.BLOCKED
