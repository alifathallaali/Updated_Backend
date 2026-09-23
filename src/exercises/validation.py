from __future__ import annotations
import pandas as pd
from .availability import resolve_column

def validate_sales_trend(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    period = resolve_column(df, "period")
    value = resolve_column(df, "sales_value")
    if period is None:
        errors.append("period is required")
    if value is None:
        errors.append("sales_value is required")
    if errors:
        return errors
    periods = pd.to_datetime(df[period], errors="coerce").dropna().nunique()
    if periods < 2:
        errors.append("at least two valid periods are required")
    numeric = pd.to_numeric(df[value], errors="coerce")
    if numeric.notna().sum() < 2:
        errors.append("at least two numeric sales_value observations are required")
    return errors
