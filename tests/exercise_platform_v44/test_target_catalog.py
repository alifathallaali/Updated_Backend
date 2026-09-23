from src.exercises.catalog.target import TARGET_EXERCISE_DEFINITIONS
from src.exercises.registry import registry


def test_target_catalog_has_14_unique_ids():
    ids = [d.id for d in TARGET_EXERCISE_DEFINITIONS]
    assert ids == [f"TGT-{i:03d}" for i in range(1, 15)]
    assert len(ids) == len(set(ids))


def test_target_catalog_is_registered():
    for definition in TARGET_EXERCISE_DEFINITIONS:
        registered = registry.get(definition.id)
        assert registered.name == definition.name
        assert registered.version == "1.0"


def test_target_catalog_reuses_existing_target_capability_metadata():
    for definition in TARGET_EXERCISE_DEFINITIONS:
        assert definition.domain == "Smart Target Planning"
        assert definition.engines == ("target_planning",)
        assert definition.data_classification == "INTERNAL"
