from src.exercises.semantic_verification import verify_str_004


def test_semantic_verification_promotes_only_verified_contracts():
    rows = {r.exercise_id: r for r in verify_str_004()}
    assert rows["MKT-003"].status == "VERIFIED"
    assert rows["MKT-010"].status == "VERIFIED"
    assert rows["MKT-004"].status == "CANDIDATE"
    assert rows["EXE-018"].status == "VERIFIED"
    assert rows["EXE-018"].checks["output_semantics"] is True
