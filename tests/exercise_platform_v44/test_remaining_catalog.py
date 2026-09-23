from src.exercises.registry import registry
from src.exercises.catalog.trade import TRADE_EXERCISE_DEFINITIONS
from src.exercises.catalog.events import EVENT_EXERCISE_DEFINITIONS
from src.exercises.catalog.medical import MEDICAL_EXERCISE_DEFINITIONS
from src.exercises.catalog.executive import EXECUTIVE_EXERCISE_DEFINITIONS
from src.exercises.catalog.strategic import STRATEGIC_EXERCISE_DEFINITIONS

CASES = [
    (TRADE_EXERCISE_DEFINITIONS, "TRD", 15, "Trade & Distribution"),
    (EVENT_EXERCISE_DEFINITIONS, "EVT", 15, "Events & Activities Intelligence"),
    (MEDICAL_EXERCISE_DEFINITIONS, "MED", 15, "Medical Affairs"),
    (EXECUTIVE_EXERCISE_DEFINITIONS, "EXE", 15, "Executive Intelligence"),
    (STRATEGIC_EXERCISE_DEFINITIONS, "STR", 10, "Strategic Decision Support"),
]

def test_remaining_catalog_ids_registration_and_metadata():
    for definitions, prefix, count, domain in CASES:
        ids = [d.id for d in definitions]
        assert ids == [f"{prefix}-{i:03d}" for i in range(1, count + 1)]
        assert len(ids) == len(set(ids))
        for definition in definitions:
            assert definition.domain == domain
            assert registry.get(definition.id).version == "1.0"
            assert definition.data_classification == "INTERNAL"

def test_catalog_does_not_claim_unverified_engine_bindings():
    for definitions, _, _, _ in CASES:
        for definition in definitions:
            assert "semantic verification" in definition.methodology.lower()

def test_str_004_is_canonical_composite():
    definition = registry.get("STR-004")
    assert definition.name == "Brand Growth Strategy"
    assert definition.type.value == "COMPOSITE"
