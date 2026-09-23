from app.engines.exercise_manifest import EXERCISE_MANIFESTS, MANIFEST_BY_ID
from app.engines.engine_registry import ENGINE_REGISTRY
from app.engines.product_catalog import PRODUCT_CATALOG
from app.visualization.exercise_catalog import EXERCISE_CATALOG

def test_manifest_is_current_metadata_source_of_truth():
    ids={m.id for m in EXERCISE_MANIFESTS}
    assert ids==set(ENGINE_REGISTRY)==set(EXERCISE_CATALOG)=={p["id"] for p in PRODUCT_CATALOG}

def test_manifest_ids_are_unique():
    assert len(MANIFEST_BY_ID)==len(EXERCISE_MANIFESTS)

def test_manifest_has_ui_and_report_contract():
    for m in EXERCISE_MANIFESTS:
        assert m.name and m.domain and m.family and m.personas
        assert m.table and m.report_section and m.readiness
        assert m.chart_patterns

def test_additional_input_exercises_declare_optional_fields():
    for m in EXERCISE_MANIFESTS:
        if m.readiness=="additional_inputs":
            assert m.optional_inputs
