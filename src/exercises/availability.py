from __future__ import annotations
import pandas as pd
from .schemas import DataAvailability, ExerciseDefinition
from .types import DataAvailabilityStatus

_ALIASES = {
    "period": {"period", "month", "period_month", "date", "month_year", "month/year"},
    "sales_value": {"sales value", "sales_value", "salesvalue", "value", "revenue"},
    "sales_units": {"sales units", "sales_units", "salesunits", "units"},
}

def _norm(value: object) -> str:
    return str(value).strip().lower().replace("_", " ")

def resolve_column(df: pd.DataFrame, logical: str) -> str | None:
    aliases = _ALIASES.get(logical, {logical})
    normalized = {_norm(c): c for c in df.columns}
    for alias in aliases:
        if alias in normalized:
            return normalized[alias]
    return None

def check_availability(df: pd.DataFrame, definition: ExerciseDefinition) -> DataAvailability:
    resolved = []
    missing = []
    for logical in definition.required_inputs:
        col = resolve_column(df, logical)
        if col is None:
            missing.append(logical)
        else:
            resolved.append(col)
    coverage = (len(resolved) / len(definition.required_inputs) * 100) if definition.required_inputs else 100.0
    if missing:
        status = DataAvailabilityStatus.INSUFFICIENT if not resolved else DataAvailabilityStatus.PARTIAL
    else:
        status = DataAvailabilityStatus.COMPLETE
    warnings = (f"Missing required inputs: {', '.join(missing)}",) if missing else ()
    return DataAvailability(status, tuple(definition.required_inputs), tuple(resolved), tuple(missing), round(coverage, 2), warnings)
