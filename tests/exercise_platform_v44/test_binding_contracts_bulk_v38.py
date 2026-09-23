from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract

NEW_IDS = {"SAL-003","MED-002","MED-003","MED-009","MED-010"}
# Historical v3.8 audit rejections that remain rejected after the approved final
# Scientific Office closure wave. MED-001/MED-007/MED-008 were subsequently
# re-reviewed and explicitly approved in the later closure delta, so this
# historical regression must not veto that authoritative later decision.
STILL_REJECTED_AS_NOT_EXACT = {"SAL-015","FIN-012"}


def test_v38_exact_bindings_present():
    assert NEW_IDS <= set(EXACT_BINDINGS)


def test_v38_exact_bindings_are_runtime_verified():
    checks = [check_binding_contract(EXACT_BINDINGS[x]) for x in sorted(NEW_IDS)]
    assert all(c.status == "VERIFIED" for c in checks), [(c.exercise_id, c.reason) for c in checks]


def test_semantically_non_exact_candidates_are_not_promoted_unless_later_approved():
    assert not (STILL_REJECTED_AS_NOT_EXACT & set(EXACT_BINDINGS))
    assert "MKT-011" not in EXACT_BINDINGS
    assert "SAL-012" not in EXACT_BINDINGS
