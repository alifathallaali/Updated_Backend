from src.exercises.semantic_verification import verify_str_004


def test_runtime_compatible_candidates_are_not_auto_promoted():
    rows = {r.exercise_id: r for r in verify_str_004()}
    assert rows["MKT-003"].status in {"CANDIDATE", "VERIFIED"}
    assert rows["MKT-004"].status == "CANDIDATE"
    assert rows["MKT-010"].status == "VERIFIED"


def test_unmapped_exe_018_remains_blocked():
    rows = {r.exercise_id: r for r in verify_str_004()}
    assert rows["EXE-018"].status == "VERIFIED"


def test_candidate_requires_definition_and_output_semantics():
    row = {r.exercise_id: r for r in verify_str_004()}["MKT-004"]
    assert row.checks["import"] is True
    assert row.checks["signature"] is True
    assert row.checks["exercise_definition"] is True
    assert row.checks["output_semantics"] is False
