from src.exercises.catalog.catalog_status import build_catalog_status
from src.exercises.registry import registry


def test_catalog_status_does_not_fabricate_closure_from_historical_target():
    status = build_catalog_status(registry.list())
    assert status.canonical_count == 231  # runtime includes 2 legacy compatibility definitions
    assert status.target_count == 250
    assert status.gap == 19
    assert status.closure_status == "TARGET_SOURCE_REQUIRED"
    assert status.duplicate_ids == ()


def test_authoritative_target_can_close_only_when_count_matches():
    definitions = registry.list()
    status = build_catalog_status(
        definitions,
        target_count=len(definitions),
        target_provenance="AUTHORITATIVE:test-fixture",
    )
    assert status.closure_status == "COMPLETE"
    assert status.gap == 0


def test_domain_counts_sum_to_catalog_count():
    status = build_catalog_status(registry.list())
    assert sum(count for _, count in status.domains) == status.canonical_count
