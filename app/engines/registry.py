"""
Engine Registry Mapping.
Binds Product IDs to execution handlers.
"""

from typing import Any, Callable, Dict, List
from .commercial_adapters import (
    run_recommendation_adapter,
    run_gtm_adapter,
    run_commercial_finance_adapter,
)

ENGINE_REGISTRY: Dict[str, Callable[[List[Dict[str, Any]], Dict[str, Any]], Dict[str, Any]]] = {
    # Engines الحالية المسجلة لديك
    "product-15": run_recommendation_adapter,
    "product-16": run_gtm_adapter,
    "product-17": run_commercial_finance_adapter,
}


def run_product_engine(
    product_id: str,
    rows: List[Dict[str, Any]],
    input_: Dict[str, Any],
    provenance: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Execute product engine via registered adapter with provenance injection."""
    if product_id not in ENGINE_REGISTRY:
        raise ValueError(f"Product Engine '{product_id}' is not registered in ENGINE_REGISTRY.")

    engine_fn = ENGINE_REGISTRY[product_id]
    result = engine_fn(rows, input_)

    # Inject execution provenance metadata cleanly
    if provenance and isinstance(result, dict):
        result["provenance"] = {
            **(result.get("provenance") or {}),
            **provenance,
        }

    return result
