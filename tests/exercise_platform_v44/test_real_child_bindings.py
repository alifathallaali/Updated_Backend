import pandas as pd
from src.exercises.adapters import run_verified_child, binding_health
from src.exercises.types import ExerciseStatus, QualityStatus


def df():
    return pd.DataFrame([
        {"Brand Name":"A","Manufacturer":"M1","Therapeutic Class":"T1","Distribution Channel":"Hospital","Sales Value":600.0,"Sales Units":60},
        {"Brand Name":"B","Manufacturer":"M1","Therapeutic Class":"T2","Distribution Channel":"Retail","Sales Value":300.0,"Sales Units":30},
        {"Brand Name":"C","Manufacturer":"M2","Therapeutic Class":"T1","Distribution Channel":"Hospital","Sales Value":100.0,"Sales Units":10},
    ])


def test_real_market_share_brand():
    r = run_verified_child("MKT-003", df())
    assert r.status == ExerciseStatus.COMPLETED
    assert r.quality_status == QualityStatus.PASS
    assert r.result.metrics[0]["value"] == 3


def test_real_market_summary():
    r = run_verified_child("MKT-004", df())
    assert r.status == ExerciseStatus.COMPLETED
    assert any(m["id"] == "total_sales" and m["value"] == 1000.0 for m in r.result.metrics)


def test_real_manufacturer_share():
    r = run_verified_child("MKT-010", df())
    assert r.status == ExerciseStatus.COMPLETED
    assert any(m["id"] == "manufacturer_count" and m["value"] == 2 for m in r.result.metrics)


def test_real_channel_performance():
    r = run_verified_child("TRD-019", df())
    assert r.status == ExerciseStatus.COMPLETED
    assert any(m["id"] == "channel_count" and m["value"] == 2 for m in r.result.metrics)


def test_unbound_child_stays_blocked():
    r = run_verified_child("MKT-011", df())
    assert r.status == ExerciseStatus.BLOCKED
    assert r.quality_status == QualityStatus.BLOCK
