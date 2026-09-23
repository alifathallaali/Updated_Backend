from src.exercises.catalog import (
    SALES_EXERCISE_DEFINITIONS, MARKETING_EXERCISE_DEFINITIONS,
    SFE_EXERCISE_DEFINITIONS, TARGET_EXERCISE_DEFINITIONS,
    HCP_KOL_EXERCISE_DEFINITIONS, BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS,
    MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS,
    PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS,
    TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS,
    MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS,
    STRATEGIC_EXERCISE_DEFINITIONS,
)
from src.exercises.catalog.canonical_audit import audit_canonical_catalog
from src.exercises.definitions_str004 import STR_004_CHILD_DEFINITIONS
from src.exercises.registry import registry


def _canonical():
    groups = (
        SALES_EXERCISE_DEFINITIONS, MARKETING_EXERCISE_DEFINITIONS,
        SFE_EXERCISE_DEFINITIONS, TARGET_EXERCISE_DEFINITIONS,
        HCP_KOL_EXERCISE_DEFINITIONS, BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS,
        MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS,
        PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS,
        TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS,
        MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS,
        STRATEGIC_EXERCISE_DEFINITIONS,
    )
    return [item for group in groups for item in group]


def test_authoritative_count_separates_catalog_from_legacy_runtime_ids():
    report = audit_canonical_catalog(_canonical(), registry.list(), STR_004_CHILD_DEFINITIONS)
    assert report.canonical_count == 229
    assert report.runtime_count == 231
    assert report.target_gap == 21
    assert report.legacy_only_ids == ("EXE-018", "TRD-019")
    assert report.duplicate_canonical_ids == ()


def test_semantic_collisions_are_explicit_not_silently_accepted():
    report = audit_canonical_catalog(_canonical(), registry.list(), STR_004_CHILD_DEFINITIONS)
    collisions = {x.exercise_id: (x.canonical_name, x.legacy_name) for x in report.semantic_collisions}
    assert collisions["MKT-004"] == ("Brand Performance", "Market Summary")
    assert collisions["MKT-010"] == ("Competitive Gap", "Manufacturer Share")
    assert report.status == "REVIEW_REQUIRED"
