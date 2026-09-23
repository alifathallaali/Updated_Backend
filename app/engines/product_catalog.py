"""Compatibility API derived from the canonical Exercise Manifest."""
from .exercise_manifest import EXERCISE_MANIFESTS, get_exercise_manifest
PRODUCT_CATALOG=[m.to_api() for m in EXERCISE_MANIFESTS]
PRODUCT_BY_ID={p["id"]:p for p in PRODUCT_CATALOG}
PRODUCT_READINESS_SUMMARY={p["id"]:p["readiness"] for p in PRODUCT_CATALOG}
def get_product_by_id(product_id: str):
    return PRODUCT_BY_ID.get(product_id)
