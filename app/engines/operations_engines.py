from ._helpers import build_output


def _numeric(row: dict, *keys: str) -> float:
    for key in keys:
        try:
            value = float(row.get(key))
            if value == value:
                return value
        except (TypeError, ValueError):
            continue
    return 0.0


def _text(row: dict, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "Unknown"


def run_supply_planning(rows: list[dict], _input: dict) -> dict:
    demand_units = sum(_numeric(r, "sales_units", "units", "demand") for r in rows)
    products = len({_text(r, "product", "brand_name") for r in rows})
    periods = len({_text(r, "period", "month") for r in rows})
    return build_output(
        "product-11", "Supply planning baseline aligned to observed product demand.",
        {"demand_units": demand_units, "products": products, "planning_periods": periods},
        [{"field": "sales_units", "value": demand_units, "source": "canonical"}],
    )


def run_inventory_optimization(rows: list[dict], _input: dict) -> dict:
    demand_units = sum(_numeric(r, "sales_units", "units", "demand") for r in rows)
    products = len({_text(r, "product", "brand_name") for r in rows})
    return build_output(
        "product-12", "Inventory optimization inputs are prepared from demand and product breadth.",
        {"demand_units": demand_units, "product_count": products, "service_level_target_pct": 95},
        [{"field": "sales_units", "value": demand_units, "source": "canonical"}],
        ["Inventory positions and lead times are required for safety-stock recommendations."],
    )


def run_sales_force_effectiveness(rows: list[dict], _input: dict) -> dict:
    territories = len({_text(r, "territory", "region") for r in rows})
    reps = len({_text(r, "sales_rep", "rep") for r in rows})
    return build_output(
        "product-13", "SFE planning structure is ready for activity and coverage inputs.",
        {"territories": territories, "sales_reps": reps, "observed_records": len(rows)},
        [{"field": "territory", "value": territories, "source": "canonical"}],
        ["Activity, representative, and territory fields are required for full SFE scoring."],
    )


def run_business_review_action_plan(rows: list[dict], _input: dict) -> dict:
    sales_value = sum(_numeric(r, "sales_value", "lc_value", "value") for r in rows)
    periods = len({_text(r, "period", "month", "year") for r in rows})
    return build_output(
        "product-14", "Business review baseline prepared with auditable period and value evidence.",
        {"sales_value": sales_value, "periods": periods, "action_items": 0},
        [{"field": "sales_value", "value": sales_value, "source": "canonical"}, {"field": "period", "value": periods, "source": "canonical"}],
        ["Action owners and due dates must be added by the workspace user."],
    )


OPERATIONS_ENGINES = {
    "product-11": run_supply_planning,
    "product-12": run_inventory_optimization,
    "product-13": run_sales_force_effectiveness,
    "product-14": run_business_review_action_plan,
}
