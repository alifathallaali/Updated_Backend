import pandas as pd
from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract
from src.exercises.runner import run_exact_bound_exercise


def sample_events():
    now = pd.Timestamp.now().normalize()
    return pd.DataFrame({
        "event_name": ["Oncology Congress", "Cardiology Workshop", "Past Symposium"],
        "type": ["Congress", "Workshop", "Symposium"],
        "date": [now + pd.Timedelta(days=30), now + pd.Timedelta(days=60), now - pd.Timedelta(days=30)],
        "city": ["Cairo", "Alexandria", "Cairo"],
        "company": ["A", "B", "A"],
        "therapy_area": ["Oncology", "Cardiology", "Oncology"],
        "budget": [100000, 50000, 75000], "currency": ["EGP"]*3,
    })


def test_event_bindings_verified():
    ids = {"EVT-001","EVT-002","EVT-003","EVT-009","EVT-010","EVT-011","EVT-014"}
    assert ids <= EXACT_BINDINGS.keys()
    assert all(check_binding_contract(EXACT_BINDINGS[i]).status == "VERIFIED" for i in ids)


def test_event_bindings_execute_through_shared_runner():
    df = sample_events()
    for exercise_id in ("EVT-001","EVT-002","EVT-003","EVT-009","EVT-010","EVT-011","EVT-014"):
        run = run_exact_bound_exercise(exercise_id=exercise_id, df=df, data_snapshot="event-test")
        assert run.status.value == "COMPLETED", (exercise_id, run.error)
        assert run.result.data_quality["binding_status"] == "VERIFIED"
        assert "events.events_intelligence" in next(iter(run.engine_versions))
