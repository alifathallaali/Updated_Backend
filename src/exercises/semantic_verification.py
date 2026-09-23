from __future__ import annotations

from dataclasses import dataclass, asdict
import importlib
import inspect
from typing import Any

from .semantic_mapping import CAPABILITY_CANDIDATES, CapabilityCandidate
from .registry import registry


@dataclass(frozen=True)
class Verification:
    exercise_id: str
    capability: str
    status: str  # VERIFIED | BLOCKED | CANDIDATE
    checks: dict[str, bool]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_candidate(candidate: CapabilityCandidate) -> Verification:
    try:
        definition = registry.get(candidate.exercise_id)
    except KeyError:
        return Verification(candidate.exercise_id, candidate.capability, "BLOCKED",
                            {"exercise_definition": False, "import": False, "callable": False, "signature": False, "output_semantics": False},
                            "Canonical ExerciseDefinition is not registered.")

    # Composite/synthesis nodes are verified as orchestration contracts, not as
    # analytics callables. They must never be treated as engines.
    if definition.type.value == "COMPOSITE" and not candidate.module:
        return Verification(candidate.exercise_id, candidate.capability or "synthesis", "VERIFIED",
                            {"exercise_definition": True, "import": True, "callable": True, "signature": True, "output_semantics": True},
                            "Validated as an evidence-synthesis node with no independent analytics engine.")

    if candidate.status == "UNMAPPED":
        return Verification(candidate.exercise_id, candidate.capability, "BLOCKED",
                            {"exercise_definition": True, "import": False, "callable": False, "signature": False, "output_semantics": False},
                            candidate.rationale or "No deterministic capability is mapped.")

    try:
        module = importlib.import_module(candidate.module)
        fn = getattr(module, candidate.callable_name)
        signature = inspect.signature(fn)
    except Exception as exc:
        return Verification(candidate.exercise_id, candidate.capability, "BLOCKED",
                            {"exercise_definition": True, "import": False, "callable": False, "signature": False, "output_semantics": False},
                            f"Existing capability is not importable: {exc}")

    accepts_dataframe = any(
        p.name in {"df", "data", "dataframe"} for p in signature.parameters.values()
    ) or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values())
    if not accepts_dataframe:
        return Verification(candidate.exercise_id, candidate.capability, "BLOCKED",
                            {"exercise_definition": True, "import": True, "callable": callable(fn), "signature": True, "output_semantics": False},
                            "Callable does not expose a dataframe-compatible input contract.")

    # For deterministic tabular capabilities, verify output semantics using a
    # minimal observed fixture. This is deliberately conservative: failure to
    # produce the declared semantic columns keeps the binding unverified.
    output_semantics = False
    try:
        import pandas as pd
        frame = pd.DataFrame({
            "Brand Name": ["A", "B"], "Manufacturer": ["M1", "M2"],
            "Sales Value": [100.0, 50.0], "Sales Units": [10.0, 5.0],
            "Therapeutic Class": ["T1", "T2"], "Distribution Channel": ["HOSPITAL", "RETAIL"],
        })
        result = fn(frame)
        columns = set(getattr(result, "columns", []))
        expected = {"Market Share"} if candidate.exercise_id in {"MKT-003", "MKT-010"} else set()
        output_semantics = bool(expected) and expected.issubset(columns)
    except Exception:
        output_semantics = False

    if output_semantics:
        return Verification(candidate.exercise_id, candidate.capability, "VERIFIED",
                            {"exercise_definition": True, "import": True, "callable": callable(fn), "signature": True, "output_semantics": True},
                            "ExerciseDefinition, callable contract and declared output semantics are validated.")

    return Verification(candidate.exercise_id, candidate.capability, "CANDIDATE",
                        {"exercise_definition": True, "import": True, "callable": callable(fn), "signature": True, "output_semantics": False},
                        "Callable is runtime-compatible, but declared output semantics are not yet validated; binding must not be promoted.")

def verify_str_004() -> list[Verification]:
    return [verify_candidate(c) for c in CAPABILITY_CANDIDATES]
