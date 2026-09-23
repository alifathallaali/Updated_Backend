from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
import pandas as pd
from .availability import check_availability, resolve_column
from .lineage import build_lineage
from .registry import registry
from .results import normalize_sales_trend_result
from .schemas import ExerciseRun
from .types import ExerciseStatus, QualityStatus, DataAvailabilityStatus
from .validation import validate_sales_trend
from .visualization import resolve_visualizations

def _run_sal_008(df: pd.DataFrame, *, definition, data_snapshot=None):
    errors = validate_sales_trend(df)
    if errors:
        raise ValueError("; ".join(errors))
    period_col = resolve_column(df, "period")
    value_col = resolve_column(df, "sales_value")
    work = pd.DataFrame({"period": pd.to_datetime(df[period_col], errors="coerce"), "sales_value": pd.to_numeric(df[value_col], errors="coerce")})
    work = work.dropna().groupby("period", as_index=False)["sales_value"].sum().sort_values("period")
    start_value = float(work.iloc[0]["sales_value"])
    end_value = float(work.iloc[-1]["sales_value"])
    growth = round(((end_value / start_value) - 1) * 100, 10) if start_value != 0 else None
    if growth is None:
        raise ValueError("Cannot calculate growth when first-period sales value is zero")
    engines = {"sales_trend_capability": "1.0"}
    lineage = build_lineage(exercise_id=definition.id, exercise_version=definition.version, data_snapshot=data_snapshot, engines=engines)
    quality = {"status": QualityStatus.PASS.value, "coverage_pct": 100.0, "observed_periods": int(len(work)), "warnings": []}
    result = normalize_sales_trend_result(rows=work.to_dict(orient="records"), start_value=start_value, end_value=end_value, growth_pct=float(growth), quality=quality, lineage=lineage)
    result.visualization_specs = resolve_visualizations(definition.id, result)
    return result

def run_exercise(df: pd.DataFrame, *, exercise_id: str = "SAL-008", user_id=None, organization_id=None,
                 market=None, data_snapshot=None, parameters=None) -> ExerciseRun:
    definition = registry.get(exercise_id)
    run = ExerciseRun(
        run_id=str(uuid4()), exercise_id=definition.id, exercise_version=definition.version,
        status=ExerciseStatus.CREATED, quality_status=QualityStatus.UNKNOWN,
        created_at=datetime.now(timezone.utc).isoformat(), user_id=user_id,
        organization_id=organization_id, market=market, data_snapshot=data_snapshot,
        engine_versions={}, parameters=parameters or {},
    )
    run.status = ExerciseStatus.DATA_CHECK
    availability = check_availability(df, definition)
    run.data_availability = availability
    if availability.status == DataAvailabilityStatus.INSUFFICIENT:
        run.status = ExerciseStatus.BLOCKED
        run.quality_status = QualityStatus.BLOCK
        run.error = "; ".join(availability.warnings)
        return run
    run.status = ExerciseStatus.VALIDATING
    try:
        run.status = ExerciseStatus.RUNNING
        if definition.id == "SAL-008":
            result = _run_sal_008(df, definition=definition, data_snapshot=data_snapshot)
        else:
            raise NotImplementedError(f"No runner registered for {definition.id}")
        run.status = ExerciseStatus.QUALITY_CHECK
        if availability.status == DataAvailabilityStatus.PARTIAL:
            result.data_quality["status"] = QualityStatus.WARNING.value
            result.data_quality["warnings"] = list(result.data_quality.get("warnings", [])) + list(availability.warnings)
            run.quality_status = QualityStatus.WARNING
            run.status = ExerciseStatus.PARTIAL
        else:
            run.quality_status = QualityStatus.PASS
            run.status = ExerciseStatus.COMPLETED
        run.result = result
        run.engine_versions = result.lineage.get("engine_versions", {})
        return run
    except Exception as exc:
        run.status = ExerciseStatus.FAILED
        run.quality_status = QualityStatus.BLOCK
        run.error = str(exc)
        return run


def run_exact_bound_exercise(*, exercise_id: str, df: pd.DataFrame | None = None,
                             parameters=None, user_id=None, organization_id=None,
                             market=None, data_snapshot=None) -> ExerciseRun:
    """Execute a catalog exercise only when it has an exact verified binding.

    This path intentionally bypasses legacy per-exercise adapters while preserving
    the shared immutable ExerciseRun envelope. It does not bypass auth/RLS; trusted
    identity context must still be supplied by the API/middleware layer.
    """
    from .executable_bindings import execute_exact_binding, BindingExecutionError
    exercise_id = exercise_id.upper()
    definition = registry.get(exercise_id)
    run = ExerciseRun(
        run_id=str(uuid4()), exercise_id=definition.id, exercise_version=definition.version,
        status=ExerciseStatus.CREATED, quality_status=QualityStatus.UNKNOWN,
        created_at=datetime.now(timezone.utc).isoformat(), user_id=user_id,
        organization_id=organization_id, market=market, data_snapshot=data_snapshot,
        engine_versions={}, parameters=dict(parameters or {}),
    )
    try:
        run.status = ExerciseStatus.RUNNING
        executed = execute_exact_binding(exercise_id, df=df, parameters=parameters, data_snapshot=data_snapshot)
        run.result = executed.result
        run.engine_versions = {executed.callable_path: "existing"}
        run.quality_status = QualityStatus.PASS
        run.status = ExerciseStatus.COMPLETED
    except BindingExecutionError as exc:
        run.status = ExerciseStatus.BLOCKED
        run.quality_status = QualityStatus.BLOCK
        run.error = str(exc)
    except Exception as exc:
        run.status = ExerciseStatus.FAILED
        run.quality_status = QualityStatus.BLOCK
        run.error = str(exc)
    return run
