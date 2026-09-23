import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.exercise_router import router
from src.exercises.binding_status import binding_status_report
from src.exercises.runner import run_exact_bound_exercise


def test_binding_status_report_is_internally_consistent():
    report = binding_status_report()
    assert report["registered_exercises"] >= 229
    assert report["exact_binding_contracts"] == report["verified_exact_bindings"] + report["blocked_exact_bindings"]
    assert report["verified_exact_bindings"] >= 37
    assert any(x["exercise_id"] == "TRD-001" and x["status"] == "VERIFIED" for x in report["checks"])


def test_trade_channel_sales_executes_existing_gtm_capability():
    df = pd.DataFrame([
        {"Distribution Channel": "Retail", "Sales Value": 100.0, "Sales Units": 10, "Brand Name": "A"},
        {"Distribution Channel": "Hospital", "Sales Value": 80.0, "Sales Units": 8, "Brand Name": "B"},
    ])
    run = run_exact_bound_exercise(exercise_id="TRD-001", df=df)
    assert run.status.value == "COMPLETED"
    assert run.result.data_quality["binding_status"] == "VERIFIED"
    assert "channel_performance" in run.result.lineage["engine_callable"]


def test_binding_status_api():
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).get("/exercises/bindings/status")
    assert response.status_code == 200
    body = response.json()
    assert body["verified_exact_bindings"] >= 37
    assert body["blocked_exact_bindings"] == 0
