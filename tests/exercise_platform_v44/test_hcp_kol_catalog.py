from src.exercises.catalog.hcp_kol import HCP_KOL_EXERCISE_DEFINITIONS
from src.exercises.registry import registry


def test_hcp_kol_catalog_has_15_unique_ids():
    ids = [d.id for d in HCP_KOL_EXERCISE_DEFINITIONS]
    assert ids == [f"HCP-{i:03d}" for i in range(1, 16)]
    assert len(ids) == len(set(ids))


def test_hcp_kol_catalog_is_registered():
    for definition in HCP_KOL_EXERCISE_DEFINITIONS:
        registered = registry.get(definition.id)
        assert registered.name == definition.name
        assert registered.version == "1.0"


def test_hcp_kol_catalog_reuses_medical_affairs_metadata():
    for definition in HCP_KOL_EXERCISE_DEFINITIONS:
        assert definition.domain == "HCP & KOL Intelligence"
        assert definition.engines == ("medical_affairs",)
        assert definition.data_classification == "INTERNAL"
