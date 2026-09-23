"""Grounding helpers for Product-13 Field Force Planner."""
from __future__ import annotations

ALIASES = {
    "territory": ("territory", "region", "area", "brick"),
    "sales_rep": ("sales_rep", "representative", "rep", "employee"),
    "hcp": ("hcp", "hcp_name", "doctor", "customer", "account"),
    "hco": ("hco", "hco_name", "hospital", "clinic", "account_name"),
    "target": ("target", "target_value", "sales_target", "quota"),
    "actual": ("actual", "actual_value", "sales_value", "achievement_value"),
    "calls": ("calls", "call_count", "visits", "visit_count", "actual_calls"),
    "planned_calls": ("planned_calls", "planned_visits", "call_plan"),
    "required_frequency": ("required_frequency", "target_frequency", "planned_frequency"),
    "potential": ("potential", "potential_score", "customer_potential", "hcp_potential", "account_potential"),
    "capacity": ("capacity", "call_capacity", "visit_capacity"),
    "period": ("period", "month", "date", "week", "year"),
    "product": ("product", "brand", "brand_name", "product_name"),
}

def present_keys(rows:list[dict], logical:str)->list[str]:
    available={str(k).strip().lower().replace(" ","_"):k for row in rows for k in row}
    return [available[k] for k in ALIASES.get(logical,(logical,)) if k in available]

def first_value(row:dict, keys:list[str]):
    for key in keys:
        value=row.get(key)
        if value is not None and str(value).strip()!="": return value
    return None

def number(value):
    try:
        v=float(value)
        return v if v==v else None
    except (TypeError,ValueError): return None
