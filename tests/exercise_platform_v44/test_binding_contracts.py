from src.exercises.catalog import CANONICAL_EXERCISE_DEFINITIONS
from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, verify_exact_bindings


def test_exact_bindings_reference_canonical_ids():
    ids = {d.id for d in CANONICAL_EXERCISE_DEFINITIONS}
    assert set(EXACT_BINDINGS).issubset(ids)


def test_exact_binding_signatures_are_healthy():
    checks = verify_exact_bindings(CANONICAL_EXERCISE_DEFINITIONS)
    assert checks
    failures = [c for c in checks if c.status != "VERIFIED"]
    assert not failures, failures


def test_bulk_verified_binding_count_is_material():
    checks = verify_exact_bindings(CANONICAL_EXERCISE_DEFINITIONS)
    assert len(checks) >= 15
