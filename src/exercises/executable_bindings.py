from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any
import pandas as pd

from .catalog.binding_contracts import EXACT_BINDINGS, BindingContract, check_binding_contract
from .schemas import CanonicalResult


class BindingExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutableBindingResult:
    exercise_id: str
    callable_path: str
    raw_output_type: str
    result: CanonicalResult


def _json_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _summarize_raw(raw: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Normalize deterministic engine output without inventing business meaning."""
    metrics: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    meta: dict[str, Any] = {}
    if isinstance(raw, pd.DataFrame):
        meta = {"row_count": int(len(raw)), "columns": [str(c) for c in raw.columns]}
        metrics.append({"id": "row_count", "value": int(len(raw)), "unit": "rows", "evidence_type": "OBSERVED"})
        findings.append({"id": "engine_output", "statement": f"Existing capability returned {len(raw)} rows.", "evidence_type": "OBSERVED"})
    elif isinstance(raw, dict):
        meta = {"keys": [str(k) for k in raw.keys()]}
        for key, value in raw.items():
            value = _json_scalar(value)
            if isinstance(value, (int, float, str, bool)) or value is None:
                metrics.append({"id": str(key), "value": value, "evidence_type": "MODELED"})
        findings.append({"id": "engine_output", "statement": "Existing capability returned a structured result.", "evidence_type": "MODELED"})
    elif isinstance(raw, (int, float, str, bool)) or raw is None:
        metrics.append({"id": "value", "value": _json_scalar(raw), "evidence_type": "MODELED"})
        findings.append({"id": "engine_output", "statement": "Existing capability returned a scalar result.", "evidence_type": "MODELED"})
    else:
        meta = {"python_type": type(raw).__name__}
        findings.append({"id": "engine_output", "statement": f"Existing capability returned {type(raw).__name__} output.", "evidence_type": "MODELED"})
    return findings, metrics, meta


def _build_kwargs(contract: BindingContract, df: pd.DataFrame | None, parameters: dict[str, Any]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    dataframe_aliases = {"df", "sales", "region_rx", "opportunity_df", "region_targets", "regional_df", "kols", "brand_scenarios"}
    missing: list[str] = []
    for name in contract.required_parameters:
        if name in parameters:
            kwargs[name] = parameters[name]
        elif name in dataframe_aliases and df is not None:
            kwargs[name] = df
        else:
            missing.append(name)
    if missing:
        raise BindingExecutionError(f"Missing execution parameters for {contract.exercise_id}: {', '.join(missing)}")
    # Optional parameters are allowed only when explicitly supplied and accepted by the callable.
    module = import_module(contract.module)
    fn = getattr(module, contract.callable_name)
    import inspect
    sig = inspect.signature(fn)
    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    for name, value in parameters.items():
        if name not in kwargs and (name in sig.parameters or accepts_kwargs):
            kwargs[name] = value
    return kwargs


def execute_exact_binding(exercise_id: str, *, df: pd.DataFrame | None = None,
                          parameters: dict[str, Any] | None = None,
                          data_snapshot: str | None = None) -> ExecutableBindingResult:
    exercise_id = exercise_id.upper()
    contract = EXACT_BINDINGS.get(exercise_id)
    if contract is None:
        raise BindingExecutionError(f"No exact semantic binding registered for {exercise_id}.")
    check = check_binding_contract(contract)
    if check.status != "VERIFIED":
        raise BindingExecutionError(check.reason)
    parameters = dict(parameters or {})
    kwargs = _build_kwargs(contract, df, parameters)
    fn = getattr(import_module(contract.module), contract.callable_name)
    # LCH-014 is bound to the existing launch intelligence capability, which
    # consumes the launch engine's prepared feature frame.  Keep preparation
    # in this thin adapter so canonical raw data can use the shared runner.
    if exercise_id in {"LCH-005", "LCH-014"} and "df" in kwargs:
        launch_module = import_module("src.engines.launch.launch")
        launch_df = launch_module.prepare_launch_data(kwargs["df"])
        launch_df = launch_module.identify_new_products(launch_df)
        launch_df = launch_module.create_launch_features(launch_df)
        kwargs["df"] = launch_df
    try:
        raw = fn(**kwargs)
    except Exception as exc:
        raise BindingExecutionError(f"Existing capability failed for {exercise_id}: {exc}") from exc
    findings, metrics, output_meta = _summarize_raw(raw)
    callable_path = f"{contract.module}.{contract.callable_name}"
    result = CanonicalResult(
        executive_summary=f"{exercise_id} executed using the verified existing PharmaLens capability {contract.callable_name}.",
        key_findings=findings,
        metrics=metrics,
        data_quality={"status": "PASS", "binding_status": "VERIFIED"},
        lineage={"exercise_id": exercise_id, "engine_callable": callable_path, "data_snapshot": data_snapshot},
        metadata={"adapter": "exact_binding", "raw_output": output_meta},
    )
    return ExecutableBindingResult(exercise_id, callable_path, type(raw).__name__, result)
