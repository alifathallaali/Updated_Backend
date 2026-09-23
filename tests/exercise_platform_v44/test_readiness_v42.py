from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.exercise_router import router
from src.exercises.readiness import exercise_readiness_report


def test_readiness_partitions_runtime_catalog_without_inflation():
    report = exercise_readiness_report()
    assert report["registered_exercises"] >= 229
    assert sum(report["counts"].values()) == report["registered_exercises"]
    assert report["counts"]["TIER_1_EXECUTABLE"] >= 38
    assert report["counts"]["COMPOSITE"] == 10
    assert 0 < report["coverage_pct"] < 100


def test_exact_verified_bindings_are_tier_one():
    report = exercise_readiness_report()
    rows = {row["exercise_id"]: row for row in report["rows"]}
    for exercise_id in ("SAL-008", "MKT-003", "FIN-008", "HCP-015", "TRD-001", "EVT-001"):
        assert rows[exercise_id]["tier"] == "TIER_1_EXECUTABLE"
        assert rows[exercise_id]["execution_path"] in {"EXACT_BINDING", "VALIDATED_VERTICAL_SLICE"}


def test_strategic_definitions_are_composite_not_fake_engine_bindings():
    report = exercise_readiness_report()
    strategic = [row for row in report["rows"] if row["exercise_id"].startswith("STR-")]
    assert len(strategic) == 10
    assert all(row["tier"] == "COMPOSITE" for row in strategic)
    assert all(row["engine_callable"] is None for row in strategic)


def test_readiness_api_is_read_only_and_returns_summary():
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/exercises/readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["counts"]["TIER_1_EXECUTABLE"] >= 38
    assert "by_domain" in body
