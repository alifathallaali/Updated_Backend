"""
PharmaLens AI - HEOR Economic Evaluation Engine
Path: PharmaLens AI V0.2/src/heor.py

Pure calculation layer. It intentionally does not duplicate PharmaLens
forecasting, scenario, market-access, finance, recommendation, or reporting.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional
import math
import numpy as np
import pandas as pd

SUPPORTED_METHODS = {"CMA", "CEA", "CUA", "CBA"}


def _number(value: Any, name: str) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric; received {value!r}.") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite; received {value!r}.")
    return x


def _method(value: str) -> str:
    value = str(value).strip().upper()
    if value not in SUPPORTED_METHODS:
        raise ValueError(f"method must be one of {sorted(SUPPORTED_METHODS)}.")
    return value


def _ratio(a: float, b: float) -> float:
    return float("nan") if np.isclose(b, 0.0) else float(a / b)


def incremental_cost(intervention_cost: float, comparator_cost: float) -> float:
    return _number(intervention_cost, "intervention_cost") - _number(
        comparator_cost, "comparator_cost"
    )


def incremental_effect(intervention_effect: float, comparator_effect: float) -> float:
    return _number(intervention_effect, "intervention_effect") - _number(
        comparator_effect, "comparator_effect"
    )


def calculate_icer(
    intervention_cost: float,
    comparator_cost: float,
    intervention_effect: float,
    comparator_effect: float,
) -> float:
    return _ratio(
        incremental_cost(intervention_cost, comparator_cost),
        incremental_effect(intervention_effect, comparator_effect),
    )


def calculate_qaly(utility: float, duration_years: float) -> float:
    utility = _number(utility, "utility")
    duration_years = _number(duration_years, "duration_years")
    if duration_years < 0:
        raise ValueError("duration_years cannot be negative.")
    return float(utility * duration_years)


def calculate_qaly_from_periods(
    utilities: Iterable[float], durations_years: Iterable[float]
) -> float:
    utilities = list(utilities)
    durations_years = list(durations_years)
    if len(utilities) != len(durations_years):
        raise ValueError("utilities and durations_years must have equal length.")
    return float(sum(calculate_qaly(u, d) for u, d in zip(utilities, durations_years)))


def calculate_nmb(effect: float, cost: float, willingness_to_pay: float) -> float:
    effect = _number(effect, "effect")
    cost = _number(cost, "cost")
    wtp = _number(willingness_to_pay, "willingness_to_pay")
    return float(effect * wtp - cost)


def calculate_incremental_nmb(
    intervention_effect: float,
    intervention_cost: float,
    comparator_effect: float,
    comparator_cost: float,
    willingness_to_pay: float,
) -> float:
    return float(
        calculate_nmb(intervention_effect, intervention_cost, willingness_to_pay)
        - calculate_nmb(comparator_effect, comparator_cost, willingness_to_pay)
    )


def classify_dominance(
    intervention_cost: float,
    comparator_cost: float,
    intervention_effect: float,
    comparator_effect: float,
) -> str:
    dc = incremental_cost(intervention_cost, comparator_cost)
    de = incremental_effect(intervention_effect, comparator_effect)
    if dc < 0 and de > 0:
        return "dominant"
    if dc > 0 and de < 0:
        return "dominated"
    if np.isclose(dc, 0.0) and np.isclose(de, 0.0):
        return "equivalent"
    return "extended_analysis_required"


def economic_evaluation(
    intervention: Mapping[str, Any],
    comparator: Mapping[str, Any],
    method: str = "CEA",
    willingness_to_pay: Optional[float] = None,
    *,
    intervention_name: str = "Intervention",
    comparator_name: str = "Comparator",
    perspective: Optional[str] = None,
    time_horizon_years: Optional[float] = None,
    currency: Optional[str] = None,
    assumptions: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    method = _method(method)
    for arm_name, arm in (("intervention", intervention), ("comparator", comparator)):
        missing = {"cost", "effect"} - set(arm)
        if missing:
            raise KeyError(f"{arm_name} missing required fields: {sorted(missing)}")

    c1 = _number(intervention["cost"], "intervention.cost")
    c0 = _number(comparator["cost"], "comparator.cost")
    e1 = _number(intervention["effect"], "intervention.effect")
    e0 = _number(comparator["effect"], "comparator.effect")
    dc, de = c1 - c0, e1 - e0

    out: Dict[str, Any] = {
        "status": "success",
        "method": method,
        "intervention": intervention_name,
        "comparator": comparator_name,
        "perspective": perspective,
        "time_horizon_years": time_horizon_years,
        "currency": currency,
        "intervention_cost": c1,
        "comparator_cost": c0,
        "intervention_effect": e1,
        "comparator_effect": e0,
        "incremental_cost": float(dc),
        "incremental_effect": float(de),
        "icer": _ratio(dc, de) if method in {"CEA", "CUA"} else float("nan"),
        "dominance": classify_dominance(c1, c0, e1, e0),
        "willingness_to_pay": None,
        "intervention_nmb": float("nan"),
        "comparator_nmb": float("nan"),
        "incremental_nmb": float("nan"),
        "assumptions": dict(assumptions or {}),
        "warnings": [],
    }

    if method == "CMA" and not np.isclose(de, 0.0):
        out["status"] = "warning"
        out["warnings"].append(
            "CMA assumes equivalent outcomes, but the supplied effects differ."
        )

    if method == "CBA":
        out["incremental_monetary_benefit"] = float(de)
        out["net_monetary_benefit_difference"] = float(de - dc)
        out["benefit_cost_ratio"] = _ratio(e1, c1)

    if willingness_to_pay is not None:
        wtp = _number(willingness_to_pay, "willingness_to_pay")
        out["willingness_to_pay"] = wtp
        out["intervention_nmb"] = calculate_nmb(e1, c1, wtp)
        out["comparator_nmb"] = calculate_nmb(e0, c0, wtp)
        out["incremental_nmb"] = float(
            out["intervention_nmb"] - out["comparator_nmb"]
        )

    return out


def compare_cost_effectiveness(
    evaluations: Iterable[Mapping[str, Any]], willingness_to_pay: float
) -> pd.DataFrame:
    records = list(evaluations)
    comparator = next((x for x in records if x.get("is_comparator")), None)
    if comparator is None:
        raise ValueError("One record must have is_comparator=True.")

    rows = []
    for item in records:
        result = economic_evaluation(
            {"cost": item["cost"], "effect": item["effect"]},
            {"cost": comparator["cost"], "effect": comparator["effect"]},
            method=item.get("method", "CEA"),
            willingness_to_pay=willingness_to_pay,
            intervention_name=str(item.get("name", "Intervention")),
            comparator_name=str(comparator.get("name", "Comparator")),
        )
        rows.append(
            {
                "Name": result["intervention"],
                "Cost": result["intervention_cost"],
                "Effect": result["intervention_effect"],
                "Incremental_Cost": result["incremental_cost"],
                "Incremental_Effect": result["incremental_effect"],
                "ICER": result["icer"],
                "NMB": result["intervention_nmb"],
                "Incremental_NMB": result["incremental_nmb"],
                "Dominance": result["dominance"],
                "Is_Comparator": bool(item.get("is_comparator", False)),
            }
        )
    return pd.DataFrame(rows)


def validate_economic_input_table(
    df: pd.DataFrame, required_columns: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    required = list(required_columns or ["Name", "Cost", "Effect"])
    missing = [c for c in required if c not in df.columns]
    numeric_issues: Dict[str, int] = {}
    for col in ("Cost", "Effect"):
        if col in df.columns:
            n = int(pd.to_numeric(df[col], errors="coerce").isna().sum())
            if n:
                numeric_issues[col] = n
    return {
        "status": "success" if not missing and not numeric_issues else "warning",
        "valid": not missing and not numeric_issues,
        "missing_columns": missing,
        "numeric_issues": numeric_issues,
        "row_count": int(len(df)),
    }


__all__ = [
    "SUPPORTED_METHODS",
    "incremental_cost",
    "incremental_effect",
    "calculate_icer",
    "calculate_qaly",
    "calculate_qaly_from_periods",
    "calculate_nmb",
    "calculate_incremental_nmb",
    "classify_dominance",
    "economic_evaluation",
    "compare_cost_effectiveness",
    "validate_economic_input_table",
]
