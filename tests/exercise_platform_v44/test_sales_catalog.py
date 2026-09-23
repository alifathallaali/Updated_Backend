from src.exercises.catalog.sales import SALES_EXERCISE_DEFINITIONS
from src.exercises.registry import registry


def test_sales_catalog_has_exact_15_ids():
    assert [d.id for d in SALES_EXERCISE_DEFINITIONS] == [f"SAL-{i:03d}" for i in range(1, 16)]


def test_sales_catalog_names_are_canonical():
    assert [d.name for d in SALES_EXERCISE_DEFINITIONS] == [
        "Sales Performance", "Actual vs Target", "Growth Analysis", "Contribution Analysis",
        "Mix Analysis", "Growth Decomposition", "Price Volume Analysis", "Sales Decline Diagnosis",
        "Sales Growth Driver", "Lost Sales Analysis", "Customer Gain Loss", "Brand Growth Driver",
        "Territory Growth Driver", "Rep Growth Driver", "Sales Forecast",
    ]


def test_registry_contains_sales_batch_without_duplicates():
    ids = [d.id for d in registry.list()]
    for i in range(1, 16):
        assert ids.count(f"SAL-{i:03d}") == 1


def test_catalog_registration_does_not_claim_unverified_engine_bindings():
    for definition in SALES_EXERCISE_DEFINITIONS:
        if definition.id != "SAL-008":
            assert "sales_trend_capability" not in definition.engines
