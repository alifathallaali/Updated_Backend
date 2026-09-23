from src.exercises.catalog import (SALES_EXERCISE_DEFINITIONS, MARKETING_EXERCISE_DEFINITIONS, SFE_EXERCISE_DEFINITIONS, TARGET_EXERCISE_DEFINITIONS, HCP_KOL_EXERCISE_DEFINITIONS, BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS, MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS, PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS, TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS, MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS, STRATEGIC_EXERCISE_DEFINITIONS)
CANONICAL_EXERCISE_DEFINITIONS = sum((SALES_EXERCISE_DEFINITIONS, MARKETING_EXERCISE_DEFINITIONS, SFE_EXERCISE_DEFINITIONS, TARGET_EXERCISE_DEFINITIONS, HCP_KOL_EXERCISE_DEFINITIONS, BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS, MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS, PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS, TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS, MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS, STRATEGIC_EXERCISE_DEFINITIONS), ())
from src.exercises.catalog.capability_audit import audit_capabilities, summarize_capability_audit


def test_audit_covers_every_canonical_definition_once():
    rows = audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS)
    assert len(rows) == len(CANONICAL_EXERCISE_DEFINITIONS)
    assert len({row.exercise_id for row in rows}) == len(rows)


def test_known_vertical_slice_bindings_are_verified():
    rows = {row.exercise_id: row for row in audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS)}
    for exercise_id in ("SAL-008", "MKT-003", "FIN-008", "HCP-015"):
        assert rows[exercise_id].status == "VERIFIED"


def test_strategic_exercises_are_not_falsely_bound_to_single_engine():
    rows = audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS)
    strategic = [row for row in rows if row.exercise_id.startswith("STR-")]
    assert strategic
    assert all(row.status == "NOT_APPLICABLE" for row in strategic)


def test_summary_is_exhaustive():
    rows = audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS)
    summary = summarize_capability_audit(rows)
    assert sum(summary.values()) == len(rows)
