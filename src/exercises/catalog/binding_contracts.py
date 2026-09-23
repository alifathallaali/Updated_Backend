from __future__ import annotations

from dataclasses import dataclass
import inspect
from importlib import import_module
from typing import Iterable

from ..schemas import ExerciseDefinition


@dataclass(frozen=True)
class BindingContract:
    exercise_id: str
    module: str
    callable_name: str
    required_parameters: tuple[str, ...] = ()
    output_kind: str = "ANY"  # DATAFRAME | DICT | SCALAR | ANY
    rationale: str = ""


@dataclass(frozen=True)
class BindingCheck:
    exercise_id: str
    status: str  # VERIFIED | CANDIDATE | BLOCKED
    module: str
    callable_name: str
    reason: str


# Conservative exact semantic bindings to deterministic functions that already
# exist in PharmaLens.  This table never creates business logic; it only maps a
# canonical exercise to an existing callable whose purpose matches the exercise.
EXACT_BINDINGS: dict[str, BindingContract] = {
    # Smart Target Planning
    "TGT-001": BindingContract("TGT-001", "src.engines.target_planning.target_engine", "calculate_company_baseline", ("sales",)),
    "TGT-002": BindingContract("TGT-002", "src.engines.target_planning.target_engine", "company_target", ("sales", "base_year", "target_year")),
    "TGT-003": BindingContract("TGT-003", "src.engines.target_planning.target_engine", "product_baseline", ("sales", "base_year"), "DATAFRAME"),
    "TGT-004": BindingContract("TGT-004", "src.engines.target_planning.target_engine", "build_product_targets", ("sales", "base_year", "target_year"), "DATAFRAME"),
    "TGT-005": BindingContract("TGT-005", "src.engines.target_planning.target_engine", "build_region_opportunity", ("region_rx",), "DATAFRAME"),
    "TGT-006": BindingContract("TGT-006", "src.engines.target_planning.target_engine", "top_down", ("company_target_dict", "opportunity_df"), "DATAFRAME"),
    "TGT-007": BindingContract("TGT-007", "src.engines.target_planning.target_engine", "bottom_up", ("region_targets",)),
    "TGT-008": BindingContract("TGT-008", "src.engines.target_planning.target_engine", "iterative_reconcile", ("company_target_dict", "regional_df"), "DATAFRAME"),
    "TGT-013": BindingContract("TGT-013", "src.engines.target_planning.target_engine", "explain_target", ("row",)),
    # Launch Intelligence — exact post-launch analytics already implemented
    "LCH-007": BindingContract("LCH-007", "src.engines.launch.launch", "calculate_launch_risk", ("product_launch", "benchmark")),
    "LCH-014": BindingContract("LCH-014", "src.engines.launch.launch", "build_launch_intelligence", ("df",), "DATAFRAME"),
    # Market / Marketing — exact descriptive market intelligence callables
    "MKT-003": BindingContract("MKT-003", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", ("df",), "DATAFRAME"),
    "MKT-004": BindingContract("MKT-004", "src.engines.market_intelligence.market_intelligence", "market_summary", ("df",), "DICT"),
    "MKT-010": BindingContract("MKT-010", "src.engines.market_intelligence.market_intelligence", "market_share_by_manufacturer", ("df",), "DATAFRAME"),
    # HCP / KOL — exact Medical Affairs scoring/planning capabilities
    "HCP-015": BindingContract("HCP-015", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    # Market Access
    "MAX-004": BindingContract("MAX-004", "src.engines.market_access.market_access", "classify_access_barrier", ("formulary_status",)),
    "MAX-005": BindingContract("MAX-005", "src.engines.market_access.market_access", "classify_access_barrier", ("formulary_status",)),
    "MAX-007": BindingContract("MAX-007", "src.engines.market_access.market_access", "price_access_tradeoff", ("price", "expected_volume", "access_probability_pct")),
    "MAX-009": BindingContract("MAX-009", "src.engines.market_access.market_access", "tender_opportunity_score", ("df",), "DATAFRAME"),
    "MAX-010": BindingContract("MAX-010", "src.engines.market_access.market_access", "hospital_segmentation", ("df",), "DATAFRAME"),
    "MAX-014": BindingContract("MAX-014", "src.engines.market_access.market_access", "build_account_plan", ("account",), "DICT"),
    # Finance
    "FIN-008": BindingContract("FIN-008", "src.engines.commercial_finance.commercial_finance", "price_volume_analysis", ("base_price", "base_volume", "new_price", "new_volume"), "DICT"),
    "FIN-013": BindingContract("FIN-013", "src.engines.commercial_finance.commercial_finance", "reforecast_ytd", ("ytd_actual", "months_elapsed", "annual_target")),
    "FIN-014": BindingContract("FIN-014", "src.engines.commercial_finance.commercial_finance", "fx_impact", ("foreign_sales", "old_fx", "new_fx")),
    "FIN-015": BindingContract("FIN-015", "src.engines.commercial_finance.commercial_finance", "incentive_multiplier", ("achievement",)),
}


def check_binding_contract(contract: BindingContract) -> BindingCheck:
    try:
        module = import_module(contract.module)
        fn = getattr(module, contract.callable_name)
        sig = inspect.signature(fn)
    except Exception as exc:
        return BindingCheck(contract.exercise_id, "BLOCKED", contract.module, contract.callable_name, f"Existing callable unavailable: {exc}")
    if not callable(fn):
        return BindingCheck(contract.exercise_id, "BLOCKED", contract.module, contract.callable_name, "Mapped object is not callable.")
    params = sig.parameters
    missing = [name for name in contract.required_parameters if name not in params and not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())]
    if missing:
        return BindingCheck(contract.exercise_id, "BLOCKED", contract.module, contract.callable_name, f"Required callable parameters missing: {', '.join(missing)}")
    return BindingCheck(contract.exercise_id, "VERIFIED", contract.module, contract.callable_name, "Canonical exercise semantics match an existing deterministic callable and its required signature is present.")


def verify_exact_bindings(definitions: Iterable[ExerciseDefinition]) -> tuple[BindingCheck, ...]:
    known = {d.id for d in definitions}
    return tuple(check_binding_contract(c) for exercise_id, c in EXACT_BINDINGS.items() if exercise_id in known)

# Expanded exact bindings to existing deterministic capabilities.
EXACT_BINDINGS.update({
    # Forecasting / sales
    "SAL-003": BindingContract("SAL-003", "src.engines.forecasting.forecasting", "calculate_market_growth", ("df",), "DATAFRAME"),
    # Commercial finance: only where the existing callable semantics are exact.
    # Medical Affairs
    "MED-002": BindingContract("MED-002", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    "MED-003": BindingContract("MED-003", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    "MED-009": BindingContract("MED-009", "src.engines.medical_affairs.medical_affairs_intelligence", "evidence_landscape", ("df",), "DATAFRAME"),
    "MED-010": BindingContract("MED-010", "src.engines.medical_affairs.medical_affairs_intelligence", "publication_intelligence", ("df",), "DATAFRAME"),
})

# Events & Activities Intelligence — productionized from Project 16 notebook into the existing empty events package.
EXACT_BINDINGS.update({
    "EVT-001": BindingContract("EVT-001", "src.engines.events.events_intelligence", "event_portfolio_review", ("df",), "DICT"),
    "EVT-002": BindingContract("EVT-002", "src.engines.events.events_intelligence", "event_calendar", ("df",), "DATAFRAME"),
    "EVT-003": BindingContract("EVT-003", "src.engines.events.events_intelligence", "event_budget_review", ("df",), "DATAFRAME"),
    "EVT-009": BindingContract("EVT-009", "src.engines.events.events_intelligence", "event_geographic_coverage", ("df",), "DATAFRAME"),
    "EVT-010": BindingContract("EVT-010", "src.engines.events.events_intelligence", "event_therapeutic_coverage", ("df",), "DATAFRAME"),
    "EVT-011": BindingContract("EVT-011", "src.engines.events.events_intelligence", "event_type_mix", ("df",), "DATAFRAME"),
    "EVT-014": BindingContract("EVT-014", "src.engines.events.events_intelligence", "event_opportunity_calendar", ("df",), "DATAFRAME"),
})

# Trade & Distribution — exact existing GTM capability.
EXACT_BINDINGS.update({
    "TRD-001": BindingContract("TRD-001", "src.engines.gtm.gtm", "channel_performance", ("df",), "DATAFRAME"),
})

# v4.3 — additional exact semantic bindings where existing callable purpose matches the canonical exercise.
EXACT_BINDINGS.update({
    # Market intelligence / trade
    "MKT-006": BindingContract("MKT-006", "src.engines.market_intelligence.market_intelligence", "market_share_by_therapeutic_class", ("df",), "DATAFRAME"),
    "TRD-013": BindingContract("TRD-013", "src.engines.gtm.gtm", "channel_performance", ("df",), "DATAFRAME"),
    # Market access
    "MAX-001": BindingContract("MAX-001", "src.engines.market_access.market_access", "institution_prioritization", ("df",), "DATAFRAME"),
    "MAX-002": BindingContract("MAX-002", "src.engines.market_access.market_access", "stakeholder_priority", ("df",), "DATAFRAME"),
    "MAX-003": BindingContract("MAX-003", "src.engines.market_access.market_access", "classify_access_barrier", ("formulary_status",)),
    "MAX-012": BindingContract("MAX-012", "src.engines.market_access.market_access", "listing_opportunity_score", ("df",), "DATAFRAME"),
    # Commercial finance
    "FIN-001": BindingContract("FIN-001", "src.engines.commercial_finance.commercial_finance", "build_budget", ("target_gross_sales", "gtn_rate", "cogs_rate", "commercial_spend"), "DICT"),
    "FIN-005": BindingContract("FIN-005", "src.engines.commercial_finance.commercial_finance", "gtn_net_price", ("gross_sales", "units", "gtn_rate"), "DICT"),
    "FIN-011": BindingContract("FIN-011", "src.engines.commercial_finance.commercial_finance", "commercial_decision", ("achievement", "roci", "commercial_spend"), "DICT"),
    # Medical affairs
    "MED-011": BindingContract("MED-011", "src.engines.medical_affairs.medical_affairs_intelligence", "clinical_trial_landscape", ("df",), "DATAFRAME"),
})

# Closure Wave 2B — approved highest-confidence existing-capability bindings only.
EXACT_BINDINGS.update({
    # Direct binds
    "MKT-001": BindingContract("MKT-001", "src.engines.market_intelligence.market_intelligence", "market_summary", ("df",), "DICT"),
    "MKT-002": BindingContract("MKT-002", "src.engines.forecasting.forecasting", "calculate_market_growth", ("df",), "DATAFRAME"),
    "PRT-009": BindingContract("PRT-009", "src.engines.scenario_planning.scenario", "run_brand_scenarios", ("df",), "DATAFRAME"),
    # Thin adapters — input/output shaping only; no new methodology.
    "HCP-010": BindingContract("HCP-010", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    "HCP-011": BindingContract("HCP-011", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    "HCP-012": BindingContract("HCP-012", "src.engines.medical_affairs.medical_affairs_intelligence", "advisory_board_plan", ("kols",), "DATAFRAME"),
    "MED-001": BindingContract("MED-001", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", ("df",), "DATAFRAME"),
    "MED-007": BindingContract("MED-007", "src.engines.medical_affairs.medical_affairs_intelligence", "advisory_board_plan", ("kols",), "DATAFRAME"),
    "MED-008": BindingContract("MED-008", "src.engines.medical_affairs.medical_affairs_intelligence", "medical_education_opportunities", ("df",), "DATAFRAME"),
    "MAX-006": BindingContract("MAX-006", "src.engines.medical_affairs.medical_affairs_intelligence", "evidence_landscape", ("df",), "DATAFRAME"),
    "PRT-005": BindingContract("PRT-005", "src.engines.scenario_planning.scenario", "add_opportunity_scores", ("brand_scenarios",), "DATAFRAME"),
})

# Final Scientific Office High-Confidence Quick-Win Wave — approved 14 only.
EXACT_BINDINGS.update({
    "SAL-001": BindingContract("SAL-001", "src.engines.company.company", "company_performance", ("df",), "DATAFRAME"),
    "SAL-004": BindingContract("SAL-004", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", ("df",), "DATAFRAME"),
    "MKT-009": BindingContract("MKT-009", "src.engines.market_intelligence.market_intelligence", "market_share_by_manufacturer", ("df",), "DATAFRAME"),
    "LCH-005": BindingContract("LCH-005", "src.engines.launch.launch", "calculate_launch_growth", ("df",), "DATAFRAME"),
    "PRT-001": BindingContract("PRT-001", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", ("df",), "DATAFRAME"),
    "PRT-003": BindingContract("PRT-003", "src.engines.gtm.gtm", "market_category_performance", ("df",), "DATAFRAME"),
    "PRT-004": BindingContract("PRT-004", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", ("df",), "DATAFRAME"),
    "PRT-014": BindingContract("PRT-014", "src.engines.market_intelligence.market_intelligence", "market_share_by_therapeutic_class", ("df",), "DATAFRAME"),
    "FIN-006": BindingContract("FIN-006", "src.engines.market_intelligence.market_intelligence", "market_summary", ("df",), "DICT"),
    "TRD-002": BindingContract("TRD-002", "src.engines.gtm.gtm", "channel_performance", ("df",), "DATAFRAME"),
    "TRD-010": BindingContract("TRD-010", "src.engines.gtm.gtm", "channel_performance", ("df",), "DATAFRAME"),
    "EXE-001": BindingContract("EXE-001", "src.engines.company.company", "company_performance", ("df",), "DATAFRAME"),
    "EXE-003": BindingContract("EXE-003", "src.engines.market_intelligence.market_intelligence", "market_summary", ("df",), "DICT"),
    "EXE-004": BindingContract("EXE-004", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", ("df",), "DATAFRAME"),
})
