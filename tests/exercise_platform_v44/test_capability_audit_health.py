from src.exercises.catalog import CANONICAL_EXERCISE_DEFINITIONS
from src.exercises.catalog.capability_audit import audit_capabilities, summarize_capability_audit


def test_deterministic_engine_packages_are_visible_to_audit():
    rows = audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS)
    by_domain = {}
    for row in rows:
        by_domain.setdefault(row.domain, []).append(row)
    for domain in ("Smart Target Planning", "Market Access", "Launch Excellence"):
        assert any(r.status == "CANDIDATE" for r in by_domain[domain])


def test_current_authoritative_capability_counts():
    summary = summarize_capability_audit(audit_capabilities(CANONICAL_EXERCISE_DEFINITIONS))
    assert summary == {"VERIFIED": 4, "CANDIDATE": 200, "UNMAPPED": 15, "NOT_APPLICABLE": 10}
