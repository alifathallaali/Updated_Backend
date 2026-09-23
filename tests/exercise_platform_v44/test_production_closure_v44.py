from src.exercises.production_closure import production_closure_report


def test_production_closure_is_fail_closed_and_separates_canonical_from_runtime():
    report = production_closure_report()
    assert report["registered_runtime_definitions"] == 231
    assert report["canonical_definitions"] == 229
    assert report["canonical_target_gap"] == 21
    assert report["exact_bindings"] >= 48
    assert report["verified_exact_bindings"] == report["exact_bindings"]
    assert report["blocked_exact_bindings"] == 0
    assert report["tier_counts"]["TIER_1_EXECUTABLE"] >= 49
    assert report["tier_counts"]["COMPOSITE"] == 10
    assert report["principles"]["new_duplicate_analytics_engines"] == 0
    assert report["release_gate"] == "READY_WITH_DOCUMENTED_GAPS"


def test_production_closure_api_is_read_only_and_available():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.api.exercise_router import router
    app = FastAPI(); app.include_router(router)
    response = TestClient(app).get('/exercises/production-closure')
    assert response.status_code == 200
    body = response.json()
    assert body['canonical_definitions'] == 229
    assert body['verified_exact_bindings'] == body['exact_bindings']
