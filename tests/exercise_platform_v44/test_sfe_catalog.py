from src.exercises.catalog.sfe import SFE_EXERCISE_DEFINITIONS
from src.exercises.registry import registry


def test_sfe_catalog_has_20_unique_ids():
    ids = [d.id for d in SFE_EXERCISE_DEFINITIONS]
    assert ids == [f"SFE-{i:03d}" for i in range(1, 21)]
    assert len(ids) == len(set(ids))


def test_sfe_catalog_is_registered():
    for definition in SFE_EXERCISE_DEFINITIONS:
        registered = registry.get(definition.id)
        assert registered.name == definition.name
        assert registered.version == "1.0"


def test_sfe_catalog_is_metadata_only():
    for definition in SFE_EXERCISE_DEFINITIONS:
        assert definition.domain == "Sales Force Effectiveness"
        assert definition.business_question
        assert definition.data_classification == "INTERNAL"
