from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract

EXPECTED = {
    "LCH-007", "LCH-014", "MKT-003", "MKT-004", "MKT-010", "HCP-015",
}

def test_expanded_exact_bindings_are_present():
    assert EXPECTED <= set(EXACT_BINDINGS)

def test_expanded_exact_bindings_verify_against_existing_callables():
    checks = [check_binding_contract(EXACT_BINDINGS[x]) for x in sorted(EXPECTED)]
    assert all(c.status == "VERIFIED" for c in checks), checks
