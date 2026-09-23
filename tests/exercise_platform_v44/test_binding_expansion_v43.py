from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract
from src.exercises.binding_status import binding_status_report
from src.exercises.readiness import exercise_readiness_report

NEW_V43 = {
    "MKT-006", "TRD-013", "MAX-001", "MAX-002", "MAX-003", "MAX-012",
    "FIN-001", "FIN-005", "FIN-011", "MED-011",
}


def test_v43_bindings_are_present_and_verified():
    assert NEW_V43 <= set(EXACT_BINDINGS)
    for exercise_id in NEW_V43:
        check = check_binding_contract(EXACT_BINDINGS[exercise_id])
        assert check.status == "VERIFIED", (exercise_id, check.reason)


def test_binding_status_has_no_blocked_exact_bindings():
    report = binding_status_report()
    assert report["exact_binding_contracts"] >= 48
    assert report["verified_exact_bindings"] == report["exact_binding_contracts"]
    assert report["blocked_exact_bindings"] == 0


def test_readiness_tier_one_expands_without_changing_catalog_size():
    report = exercise_readiness_report()
    assert report["registered_exercises"] == 231
    assert report["counts"]["TIER_1_EXECUTABLE"] >= 49
    assert report["counts"]["COMPOSITE"] == 10
