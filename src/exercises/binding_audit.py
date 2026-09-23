from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any
import importlib

from .adapters import VERIFIED_BINDINGS, binding_health
from .orchestrator import STR_004


@dataclass(frozen=True)
class BindingAudit:
    exercise_id: str
    registered: bool
    import_healthy: bool
    module: str | None
    callable_name: str | None
    capability: str | None
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def audit_exercise(exercise_id: str) -> BindingAudit:
    binding = VERIFIED_BINDINGS.get(exercise_id.upper())
    if binding is None:
        return BindingAudit(exercise_id, False, False, None, None, None, "No verified binding registered; semantic mapping required before execution.")
    health = binding_health(exercise_id)
    return BindingAudit(
        exercise_id=exercise_id,
        registered=True,
        import_healthy=bool(health.get("available")),
        module=health.get("module"),
        callable_name=health.get("callable"),
        capability=health.get("capability"),
        reason=health.get("reason"),
    )


def audit_str_004() -> list[BindingAudit]:
    ids = (*STR_004.required_children, *STR_004.optional_children, *((STR_004.synthesis_node,) if STR_004.synthesis_node else ()))
    return [audit_exercise(exercise_id) for exercise_id in ids]


def available_engine_callables(module_name: str) -> list[str]:
    """Read-only introspection helper; it never selects a binding automatically."""
    module = importlib.import_module(module_name)
    return sorted(name for name, value in vars(module).items() if callable(value) and not name.startswith("_"))
