from app.engines.engine_registry import ENGINE_REGISTRY,list_registered_engines
from app.engines.product_catalog import PRODUCT_CATALOG,PRODUCT_READINESS_SUMMARY
from app.visualization.exercise_catalog import EXERCISE_CATALOG
def test_registry_invariant():
 ids={p["id"] for p in PRODUCT_CATALOG}
 assert ids==set(ENGINE_REGISTRY)==set(PRODUCT_READINESS_SUMMARY)==set(EXERCISE_CATALOG)==set(list_registered_engines())
def test_15_to_17_are_canonical(): assert {"product-15","product-16","product-17"} <= set(ENGINE_REGISTRY)
