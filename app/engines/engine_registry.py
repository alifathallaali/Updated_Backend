from .analytics_engines import ANALYTICS_ENGINES
from .operations_engines import OPERATIONS_ENGINES
from .product_catalog import get_product_by_id
from .strategy_engines import STRATEGY_ENGINES

ENGINE_REGISTRY = {**ANALYTICS_ENGINES, **STRATEGY_ENGINES, **OPERATIONS_ENGINES}

VERIFIED_NOTEBOOK_SUBSETS = {"product-01", "product-02", "product-03", "product-05", "product-06", "product-07", "product-08"}


def run_product_engine(product_id: str, rows: list[dict], input_: dict) -> dict:
    engine = ENGINE_REGISTRY.get(product_id)
    if not engine:
        raise ValueError(f"No engine registered for {product_id}")
    result = engine(rows, input_)
    definition = get_product_by_id(product_id)
    has_verified_subset = product_id in VERIFIED_NOTEBOOK_SUBSETS
    readiness_state = (
        "verified_subset" if has_verified_subset else
        "additional_inputs" if definition and definition["status"] == "in_progress" else
        "foundation_only"
    )
    readiness_warning = (
        "Verified notebook subset is available; optional notebook outputs may still require additional fields."
        if has_verified_subset else
        "This output is an input-readiness baseline; additional operational fields are required before recommendations."
        if readiness_state == "additional_inputs" else
        "No complete product-specific notebook routine is available for this product; this output is a transparent foundation baseline."
    )
    status = "error" if result["status"] == "error" else "partial"
    warnings = list(dict.fromkeys([*result["warnings"], readiness_warning]))
    return {
        **result,
        "status": status,
        "metrics": {**result["metrics"], "readiness_state": readiness_state, "notebook_logic_scope": "verified_subset" if has_verified_subset else "foundation_adapter"},
        "warnings": warnings,
        "confidence": {**result["confidence"], "rationale": f"{result['confidence']['rationale']} Readiness state: {readiness_state}."},
    }


def list_registered_engines() -> list[str]:
    return sorted(ENGINE_REGISTRY.keys())
