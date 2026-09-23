from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import inspect
from typing import Iterable

from ..schemas import ExerciseDefinition


@dataclass(frozen=True)
class CapabilityAuditRow:
    exercise_id: str
    domain: str
    status: str  # VERIFIED | CANDIDATE | UNMAPPED | NOT_APPLICABLE
    candidate_modules: tuple[str, ...]
    declared_engines: tuple[str, ...]
    rationale: str


DOMAIN_MODULES: dict[str, tuple[str, ...]] = {
    "Sales Intelligence & Performance": ("src.engines.market_intelligence.market_intelligence", "src.engines.forecasting.forecasting", "src.engines.commercial_finance.commercial_finance"),
    "Marketing & Brand Intelligence": ("src.engines.market_intelligence.market_intelligence", "src.engines.recommendation.recommendation"),
    "Sales Force Effectiveness": ("src.engines.target_planning.target_engine",),
    "Smart Target Planning": ("src.engines.target_planning.target_engine",),
    "HCP & KOL Intelligence": ("src.engines.medical_affairs.medical_affairs_intelligence",),
    "Business Development": ("src.engines.market_intelligence.market_intelligence", "src.engines.scenario_planning.scenario"),
    "Market Access": ("src.engines.market_access.market_access",),
    "Launch Excellence": ("src.engines.launch.launch",),
    "Portfolio Strategy": ("src.engines.market_intelligence.market_intelligence", "src.engines.scenario_planning.scenario"),
    "Commercial Finance": ("src.engines.commercial_finance.commercial_finance",),
    "Trade & Distribution": ("src.engines.gtm.gtm",),
    "Events & Activities Intelligence": (),
    "Medical Affairs": ("src.engines.medical_affairs.medical_affairs_intelligence",),
    "Executive Intelligence": ("src.engines.company.company", "src.engines.market_intelligence.market_intelligence"),
    "Strategic Decision Support": ("src.engines.scenario_planning.scenario",),
}


# Only bindings already validated by the production slice belong here.
VERIFIED_IDS = frozenset({"SAL-008", "MKT-003", "FIN-008", "HCP-015"})


def _healthy_module(module_name: str) -> bool:
    try:
        module = import_module(module_name)
        return any(callable(obj) and not name.startswith("_") for name, obj in inspect.getmembers(module) if inspect.isfunction(obj))
    except Exception:
        return False


def audit_capabilities(definitions: Iterable[ExerciseDefinition]) -> tuple[CapabilityAuditRow, ...]:
    rows: list[CapabilityAuditRow] = []
    module_health: dict[str, bool] = {}
    for definition in definitions:
        modules = DOMAIN_MODULES.get(definition.domain, ())
        healthy = []
        for module in modules:
            if module not in module_health:
                module_health[module] = _healthy_module(module)
            if module_health[module]:
                healthy.append(module)
        if definition.id in VERIFIED_IDS:
            status, rationale = "VERIFIED", "Binding was validated by the existing vertical-slice semantic/integration tests."
        elif definition.id.startswith("STR-"):
            status, rationale = "NOT_APPLICABLE", "Strategic definitions are composite/orchestration exercises; engine binding is evaluated at child-capability level."
        elif healthy:
            status, rationale = "CANDIDATE", "One or more domain-relevant existing engine modules are importable; exact input/output semantics still require verification."
        else:
            status, rationale = "UNMAPPED", "No healthy domain-relevant deterministic engine module is currently mapped; no binding is inferred."
        rows.append(CapabilityAuditRow(definition.id, definition.domain, status, tuple(healthy), tuple(definition.engines), rationale))
    return tuple(rows)


def summarize_capability_audit(rows: Iterable[CapabilityAuditRow]) -> dict[str, int]:
    summary = {"VERIFIED": 0, "CANDIDATE": 0, "UNMAPPED": 0, "NOT_APPLICABLE": 0}
    for row in rows:
        summary[row.status] = summary.get(row.status, 0) + 1
    return summary
