from ..visualization import build_visualizations
from ..visualization.exercise_catalog import get_exercise_presentation
from .analytics_engines import ANALYTICS_ENGINES
from .operations_engines import OPERATIONS_ENGINES
from .product_catalog import get_product_by_id
from .strategy_engines import STRATEGY_ENGINES
from .commercial_adapters import run_recommendation_adapter, run_gtm_adapter, run_commercial_finance_adapter
from .heor_adapters import run_heor_market_access_adapter
from .hospital_procurement_adapters import run_hospital_procurement_adapter
from .field_force_adapters import run_field_force_planner_adapter
from .consumer_health_adapters import run_consumer_health_adapter
from .exercise_journey import next_exercises
from ..visualization.executive_narrative import build_executive_narrative

COMMERCIAL_ENGINES={"product-15":run_recommendation_adapter,"product-16":run_gtm_adapter,"product-17":run_commercial_finance_adapter}
HEOR_ENGINES={"product-18":run_heor_market_access_adapter}
HOSPITAL_PROCUREMENT_ENGINES={"product-19":run_hospital_procurement_adapter}
FIELD_FORCE_ENGINES={"product-13":run_field_force_planner_adapter}
CONSUMER_HEALTH_ENGINES={"product-20":run_consumer_health_adapter}
ENGINE_REGISTRY={**ANALYTICS_ENGINES,**STRATEGY_ENGINES,**OPERATIONS_ENGINES,**COMMERCIAL_ENGINES,**HEOR_ENGINES,**HOSPITAL_PROCUREMENT_ENGINES,**FIELD_FORCE_ENGINES,**CONSUMER_HEALTH_ENGINES}

VERIFIED_NOTEBOOK_SUBSETS = {"product-01", "product-02", "product-03", "product-05", "product-06", "product-07", "product-08", "product-20"}


def run_product_engine(product_id: str, rows: list[dict], input_: dict) -> dict:
    engine = ENGINE_REGISTRY.get(product_id)
    if not engine:
        raise ValueError(f"No engine registered for {product_id}")
    result = engine(rows, input_)
    definition = get_product_by_id(product_id)
    has_verified_subset = product_id in VERIFIED_NOTEBOOK_SUBSETS
    readiness_state=((definition or {}).get("readiness") or {}).get("state","verified_subset" if has_verified_subset else "foundation_only")
    readiness_warning = (
        "Verified notebook subset is available; optional notebook outputs may still require additional fields."
        if has_verified_subset else
        "This output is an input-readiness baseline; additional operational fields are required before recommendations."
        if readiness_state == "additional_inputs" else
        "No complete product-specific notebook routine is available for this product; this output is a transparent foundation baseline."
    )
    status = "error" if result["status"] == "error" else "partial"
    warnings = list(dict.fromkeys([*result["warnings"], readiness_warning]))
    enriched = {
        **result,
        "status": status,
        "metrics": {**result["metrics"], "readiness_state": readiness_state, "notebook_logic_scope": "verified_subset" if has_verified_subset else "foundation_adapter"},
        "warnings": warnings,
        "confidence": {**result["confidence"], "rationale": f"{result['confidence']['rationale']} Readiness state: {readiness_state}."},
    }
    enriched["visualizations"] = build_visualizations(product_id, rows, enriched)
    enriched["presentation"] = get_exercise_presentation(product_id, name=(definition or {}).get("name", ""), domain=(definition or {}).get("domain", ""))
    available_columns = list(rows[0].keys()) if rows else []
    enriched["next_exercises"] = next_exercises(product_id, available_columns)
    enriched["trust"] = {
        "resultType": "calculated",
        "source": "governed_dataset",
        "method": "deterministic_engine",
        "rawRowsSentToLLM": False,
        "limitations": warnings,
    }
    enriched["executive_narrative"] = build_executive_narrative(enriched,enriched["next_exercises"])
    return enriched


def list_registered_engines() -> list[str]:
    return sorted(ENGINE_REGISTRY.keys())
