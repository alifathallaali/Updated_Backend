from src.exercises.catalog.marketing import MARKETING_EXERCISE_DEFINITIONS
from src.exercises.registry import registry


def test_marketing_catalog_has_15_unique_canonical_ids():
    ids = [d.id for d in MARKETING_EXERCISE_DEFINITIONS]
    assert ids == [f"MKT-{i:03d}" for i in range(1, 16)]
    assert len(ids) == len(set(ids))


def test_marketing_catalog_is_registered():
    for definition in MARKETING_EXERCISE_DEFINITIONS:
        registered = registry.get(definition.id)
        assert registered.name == definition.name
        assert registered.version == "1.0"


def test_known_existing_str004_definitions_are_not_lost():
    assert registry.get("MKT-003").name == "Market Share"
    assert registry.get("MKT-004").name == "Brand Performance"
    assert registry.get("MKT-010").name == "Competitive Gap"
    assert registry.get("MKT-011").name == "White Space"
