from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.exercise_router import router

app = FastAPI(); app.include_router(router)
client = TestClient(app)


def test_event_exercise_executes_via_generic_api():
    r = client.post('/exercises/EVT-001/run', json={"rows": [
        {"event_name":"Oncology Congress","type":"Congress","date":"2099-01-01","city":"Cairo","therapy_area":"Oncology"},
        {"event_name":"Cardiology Workshop","type":"Workshop","date":"2099-02-01","city":"Alexandria","therapy_area":"Cardiology"}
    ]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == "EVT-001"
    assert body["status"] == "COMPLETED"
    assert body["quality_status"] == "PASS"
