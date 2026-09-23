from src.exercises.catalog.business_development import BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS
from src.exercises.catalog.reconciliation import reconcile_catalog


def test_bd_canonical_extension_is_present():
    by_id = {x.id: x.name for x in BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS}
    assert by_id["BD-016"] == "Line Extension"
    assert by_id["BD-017"] == "Commercial Feasibility"
    assert by_id["BD-018"] == "Strategic Fit"
    assert by_id["BD-019"] == "Revenue Opportunity"
    assert by_id["BD-020"] == "Investment Scenario"


def test_reconciliation_does_not_invent_missing_exercises():
    report = reconcile_catalog(BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS, target=20)
    assert report.registered_count == 20
    assert report.unresolved_target_gap == 0
    assert report.duplicate_ids == ()
    assert report.status == "COMPLETE"
