"""
PharmaLens AI - Budget Impact Analysis Engine
Path: PharmaLens AI V0.2/src/budget_impact.py

Population-based budget impact calculations for HEOR/Market Access.
This module does not replace commercial_finance.py: it models payer/budget
impact, while commercial_finance.py remains the commercial P&L/ROCI layer.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence
import math
import numpy as np
import pandas as pd


def _number(value: Any, name: str, *, non_negative: bool = False) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric; received {value!r}.") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite.")
    if non_negative and x < 0:
        raise ValueError(f"{name} cannot be negative.")
    return x


def _rate(value: Any, name: str) -> float:
    x = _number(value, name)
    if not 0 <= x <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")
    return x


def eligible_population(
    population: float,
    prevalence_rate: float,
    diagnosis_rate: float = 1.0,
    eligibility_rate: float = 1.0,
) -> Dict[str, float]:
    """Patient funnel from population to treatment-eligible patients."""
    population = _number(population, "population", non_negative=True)
    prevalence_rate = _rate(prevalence_rate, "prevalence_rate")
    diagnosis_rate = _rate(diagnosis_rate, "diagnosis_rate")
    eligibility_rate = _rate(eligibility_rate, "eligibility_rate")

    disease = population * prevalence_rate
    diagnosed = disease * diagnosis_rate
    eligible = diagnosed * eligibility_rate

    return {
        "population": population,
        "disease_population": float(disease),
        "diagnosed_population": float(diagnosed),
        "eligible_population": float(eligible),
    }


def annual_treatment_cost(
    acquisition_cost: float,
    administrations_per_year: float = 1.0,
    administration_cost_per_event: float = 0.0,
    monitoring_cost_per_year: float = 0.0,
    adverse_event_cost_per_year: float = 0.0,
    other_cost_per_year: float = 0.0,
    offsets_per_year: float = 0.0,
) -> Dict[str, float]:
    """Annual per-patient cost including offsets."""
    acquisition_cost = _number(acquisition_cost, "acquisition_cost", non_negative=True)
    administrations_per_year = _number(
        administrations_per_year, "administrations_per_year", non_negative=True
    )
    administration_cost_per_event = _number(
        administration_cost_per_event,
        "administration_cost_per_event",
        non_negative=True,
    )
    monitoring_cost_per_year = _number(
        monitoring_cost_per_year, "monitoring_cost_per_year", non_negative=True
    )
    adverse_event_cost_per_year = _number(
        adverse_event_cost_per_year,
        "adverse_event_cost_per_year",
        non_negative=True,
    )
    other_cost_per_year = _number(
        other_cost_per_year, "other_cost_per_year", non_negative=True
    )
    offsets_per_year = _number(offsets_per_year, "offsets_per_year", non_negative=True)

    drug = acquisition_cost * administrations_per_year
    administration = administration_cost_per_event * administrations_per_year
    gross = (
        drug
        + administration
        + monitoring_cost_per_year
        + adverse_event_cost_per_year
        + other_cost_per_year
    )
    net = gross - offsets_per_year

    return {
        "drug_acquisition_cost": float(drug),
        "administration_cost": float(administration),
        "monitoring_cost": monitoring_cost_per_year,
        "adverse_event_cost": adverse_event_cost_per_year,
        "other_cost": other_cost_per_year,
        "cost_offsets": offsets_per_year,
        "gross_annual_cost_per_patient": float(gross),
        "net_annual_cost_per_patient": float(net),
    }


def budget_impact_year(
    eligible_patients: float,
    uptake_rate: float,
    intervention_cost_per_patient: float,
    comparator_cost_per_patient: float,
    *,
    switching_cost_per_patient: float = 0.0,
    one_time_cost: float = 0.0,
) -> Dict[str, float]:
    """One-year incremental budget impact versus comparator."""
    eligible_patients = _number(
        eligible_patients, "eligible_patients", non_negative=True
    )
    uptake_rate = _rate(uptake_rate, "uptake_rate")
    intervention_cost = _number(
        intervention_cost_per_patient,
        "intervention_cost_per_patient",
    )
    comparator_cost = _number(
        comparator_cost_per_patient,
        "comparator_cost_per_patient",
    )
    switching_cost = _number(
        switching_cost_per_patient,
        "switching_cost_per_patient",
        non_negative=True,
    )
    one_time_cost = _number(one_time_cost, "one_time_cost", non_negative=True)

    treated = eligible_patients * uptake_rate
    remaining = eligible_patients - treated

    current_scenario_cost = eligible_patients * comparator_cost
    new_scenario_cost = (
        treated * intervention_cost
        + remaining * comparator_cost
        + treated * switching_cost
        + one_time_cost
    )
    incremental = new_scenario_cost - current_scenario_cost

    return {
        "eligible_patients": float(eligible_patients),
        "uptake_rate": uptake_rate,
        "treated_with_intervention": float(treated),
        "remaining_on_comparator": float(remaining),
        "current_scenario_cost": float(current_scenario_cost),
        "new_scenario_cost": float(new_scenario_cost),
        "incremental_budget_impact": float(incremental),
        "incremental_cost_per_eligible_patient": (
            float(incremental / eligible_patients)
            if eligible_patients > 0 else float("nan")
        ),
    }


def multi_year_budget_impact(
    eligible_patients: float,
    uptake_rates: Sequence[float],
    intervention_cost_per_patient: float,
    comparator_cost_per_patient: float,
    *,
    annual_population_growth: float = 0.0,
    switching_cost_per_patient: float = 0.0,
    one_time_cost_year_1: float = 0.0,
    discount_rate: float = 0.0,
) -> Dict[str, Any]:
    """Multi-year BIA with uptake trajectory and optional discounting."""
    eligible_patients = _number(
        eligible_patients, "eligible_patients", non_negative=True
    )
    population_growth = _number(annual_population_growth, "annual_population_growth")
    discount_rate = _number(discount_rate, "discount_rate")
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -1.")

    rows = []
    current_eligible = eligible_patients

    for year, uptake in enumerate(uptake_rates, start=1):
        if year > 1:
            current_eligible *= 1 + population_growth
            if current_eligible < 0:
                raise ValueError("Population growth produced negative population.")

        result = budget_impact_year(
            current_eligible,
            uptake,
            intervention_cost_per_patient,
            comparator_cost_per_patient,
            switching_cost_per_patient=switching_cost_per_patient,
            one_time_cost=one_time_cost_year_1 if year == 1 else 0.0,
        )
        discount_factor = (1 + discount_rate) ** (year - 1)
        result["year"] = year
        result["discount_factor"] = float(discount_factor)
        result["discounted_budget_impact"] = float(
            result["incremental_budget_impact"] / discount_factor
        )
        rows.append(result)

    table = pd.DataFrame(rows)
    return {
        "status": "success",
        "years": table,
        "cumulative_budget_impact": float(
            table["incremental_budget_impact"].sum()
        ) if not table.empty else 0.0,
        "discounted_cumulative_budget_impact": float(
            table["discounted_budget_impact"].sum()
        ) if not table.empty else 0.0,
    }


def budget_impact_scenarios(
    eligible_patients: float,
    scenarios: Mapping[str, Sequence[float]],
    intervention_cost_per_patient: float,
    comparator_cost_per_patient: float,
    **kwargs: Any,
) -> pd.DataFrame:
    """Compare multiple named uptake trajectories."""
    rows = []
    for name, uptake_rates in scenarios.items():
        result = multi_year_budget_impact(
            eligible_patients,
            uptake_rates,
            intervention_cost_per_patient,
            comparator_cost_per_patient,
            **kwargs,
        )
        rows.append(
            {
                "Scenario": name,
                "Years": len(uptake_rates),
                "Cumulative_Budget_Impact": result["cumulative_budget_impact"],
                "Discounted_Cumulative_Budget_Impact": (
                    result["discounted_cumulative_budget_impact"]
                ),
            }
        )
    return pd.DataFrame(rows)


__all__ = [
    "eligible_population",
    "annual_treatment_cost",
    "budget_impact_year",
    "multi_year_budget_impact",
    "budget_impact_scenarios",
]
