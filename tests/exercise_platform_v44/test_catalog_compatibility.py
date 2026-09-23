from src.exercises.catalog.compatibility import (
    STR004_LEGACY_ALIASES,
    compatibility_alias,
    public_catalog_id,
)


def test_str004_collision_aliases_are_explicit_and_unique():
    aliases = {x.legacy_id: x for x in STR004_LEGACY_ALIASES}
    assert set(aliases) == {"MKT-004", "MKT-010", "TRD-019", "EXE-018"}
    assert len({x.replacement_id for x in aliases.values()}) == 4
    assert aliases["MKT-004"].replacement_id.startswith("STR004-CAP-")
    assert aliases["EXE-018"].replacement_id.startswith("STR004-SYNTHESIS-")


def test_legacy_only_ids_are_not_public_catalog_ids():
    assert public_catalog_id("TRD-019") is None
    assert public_catalog_id("EXE-018") is None
    assert public_catalog_id("MKT-004") == "MKT-004"
    assert compatibility_alias("MKT-010") is not None
