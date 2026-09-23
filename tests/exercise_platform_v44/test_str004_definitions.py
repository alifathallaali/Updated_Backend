from src.exercises.definitions_str004 import STR_004_CHILD_DEFINITIONS
from src.exercises.registry import registry


def test_all_str004_children_have_canonical_definitions():
    ids = {d.id for d in STR_004_CHILD_DEFINITIONS}
    expected = {"MKT-003", "MKT-004", "MKT-010", "MKT-011", "SAL-012", "HCP-015", "TRD-019", "FIN-008", "EXE-018"}
    assert ids == expected
    assert all(registry.get(i).id == i for i in expected)


def test_exe_018_is_synthesis_definition_not_an_engine():
    d = registry.get("EXE-018")
    assert d.type.value == "COMPOSITE"
    assert d.engines == ()
