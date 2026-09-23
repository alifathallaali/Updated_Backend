"""Deterministic formatting helpers shared by UI and export layers."""
from __future__ import annotations


def compact_number(value: float | int) -> str:
    value = float(value)
    abs_value = abs(value)
    for divisor, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if abs_value >= divisor:
            return f"{value / divisor:.1f}{suffix}"
    return f"{value:,.0f}"


def percentage(value: float | int, decimals: int = 1) -> str:
    return f"{float(value):.{decimals}f}%"


def currency(value: float | int, currency_code: str = "EGP") -> str:
    return f"{currency_code} {compact_number(value)}"


def format_value(value, value_format: str = "auto", unit: str | None = None) -> str:
    if value is None:
        return "—"
    if value_format == "percent":
        return percentage(value)
    if value_format == "currency":
        return currency(value, unit or "EGP")
    if value_format == "integer":
        return f"{int(round(float(value))):,}"
    if isinstance(value, (int, float)):
        return compact_number(value)
    return str(value)
