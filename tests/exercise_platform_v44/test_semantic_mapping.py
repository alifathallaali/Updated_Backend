from src.exercises.semantic_mapping import candidates_for, inspect_candidate


def test_all_str004_children_have_explicit_mapping_state():
    expected = {"MKT-003", "MKT-004", "MKT-010", "MKT-011", "SAL-012", "HCP-015", "TRD-019", "FIN-008", "EXE-018"}
    actual = {c.exercise_id for c in sum((candidates_for(x) for x in expected), [])}
    assert actual == expected


def test_mkt003_is_verified_and_callable():
    c = candidates_for("MKT-003")[0]
    inspected = inspect_candidate(c)
    assert c.status == "VERIFIED"
    assert inspected["runtime_status"] == "READY"
    assert "df=None" in inspected["signature"]


def test_unmapped_executive_child_does_not_guess():
    c = candidates_for("EXE-018")[0]
    inspected = inspect_candidate(c)
    assert inspected["runtime_status"] == "UNMAPPED"
    assert inspected["status"] == "UNMAPPED"
