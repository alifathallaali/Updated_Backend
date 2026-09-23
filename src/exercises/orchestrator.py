from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from uuid import uuid4
from .schemas import CanonicalResult, ExerciseRun
from .types import ExerciseStatus, QualityStatus

@dataclass(frozen=True)
class CompositeDefinition:
    id: str
    version: str
    name: str
    required_children: tuple[str, ...]
    optional_children: tuple[str, ...] = ()
    synthesis_node: str | None = None

@dataclass
class CompositeRun:
    run_id: str
    composite_id: str
    composite_version: str
    status: ExerciseStatus
    quality_status: QualityStatus
    child_runs: dict[str, ExerciseRun] = field(default_factory=dict)
    result: CanonicalResult | None = None
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "composite_id": self.composite_id,
            "composite_version": self.composite_version, "status": self.status.value,
            "quality_status": self.quality_status.value,
            "child_runs": {k: v.to_dict() for k, v in self.child_runs.items()},
            "result": self.result.to_dict() if self.result else None,
            "conflicts": self.conflicts, "error": self.error,
        }


def _metric_context(metric: Mapping[str, Any]) -> tuple[Any, ...]:
    """Context key prevents false conflicts across periods/entities/units."""
    return (
        metric.get("period"), metric.get("entity"), metric.get("dimension"),
        metric.get("unit"), metric.get("currency"), metric.get("denominator"),
    )


def _collect_conflicts(child_runs: Mapping[str, ExerciseRun]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, tuple[Any, ...]], tuple[Any, str]] = {}
    conflicts: list[dict[str, Any]] = []
    for child_id, run in child_runs.items():
        if not run.result:
            continue
        for metric in run.result.metrics:
            metric_id = metric.get("id")
            if not metric_id or "value" not in metric:
                continue
            value = metric["value"]
            context = _metric_context(metric)
            key = (metric_id, context)
            if key in seen and seen[key][0] != value:
                previous_value, previous_source = seen[key]
                conflicts.append({
                    "type": "METRIC_CONFLICT",
                    "metric_id": metric_id,
                    "context": {
                        k: metric.get(k) for k in ("period", "entity", "dimension", "unit", "currency", "denominator")
                        if metric.get(k) is not None
                    },
                    "sources": [previous_source, child_id],
                    "values": [previous_value, value],
                    "resolution": "REVIEW_REQUIRED",
                })
            else:
                seen[key] = (value, child_id)
    return conflicts

def _synthesize(definition: CompositeDefinition, child_runs: Mapping[str, ExerciseRun], conflicts: list[dict[str, Any]]) -> CanonicalResult:
    findings, risks, recommendations = [], [], []
    for child_id, run in child_runs.items():
        if run.result:
            findings.extend([{**f, "source_exercise": child_id} for f in run.result.key_findings])
            risks.extend([{**r, "source_exercise": child_id} for r in run.result.risks])
            recommendations.extend([{**r, "source_exercise": child_id} for r in run.result.recommendations])
    if conflicts:
        risks.append({"id": f"{definition.id}-CONFLICT", "statement": "Conflicting child metrics were detected; they require review before synthesis is used for a decision."})
    optional_unavailable = [
        child_id for child_id in definition.optional_children
        if child_id not in child_runs or child_runs[child_id].status in {ExerciseStatus.BLOCKED, ExerciseStatus.FAILED}
    ]
    required_warning = any(
        child_runs[c].quality_status == QualityStatus.WARNING
        for c in definition.required_children if c in child_runs
    )
    quality = QualityStatus.WARNING if conflicts or optional_unavailable or required_warning else QualityStatus.PASS
    return CanonicalResult(
        executive_summary=f"{definition.name} synthesized validated evidence from {sum(1 for r in child_runs.values() if r.result)} child exercises; strategic interpretation must respect child quality and evidence.",
        key_findings=findings, risks=risks, recommendations=recommendations,
        assumptions=["Composite synthesis does not invent or recalculate child metrics."],
        data_quality={
            "status": quality.value,
            "child_count": len(child_runs),
            "completed_child_count": sum(1 for r in child_runs.values() if r.status == ExerciseStatus.COMPLETED),
            "conflict_count": len(conflicts),
            "optional_unavailable": optional_unavailable,
            "child_quality": {k: v.quality_status.value for k, v in child_runs.items()},
        },
        lineage={
            "composite_id": definition.id,
            "composite_version": definition.version,
            "child_run_ids": {k: v.run_id for k, v in child_runs.items()},
            "child_exercise_versions": {k: v.exercise_version for k, v in child_runs.items()},
            "child_data_snapshots": {k: v.data_snapshot for k, v in child_runs.items()},
            "child_engine_versions": {k: v.engine_versions for k, v in child_runs.items()},
            "synthesis_node": definition.synthesis_node,
        },
        metadata={
            "synthesis": "evidence_aggregation_only",
            "evidence_sources": sorted(k for k, v in child_runs.items() if v.result is not None),
            "conflicts_require_review": bool(conflicts),
        },
    )


def run_composite(definition: CompositeDefinition, *, child_runner: Callable[[str], ExerciseRun]) -> CompositeRun:
    output = CompositeRun(str(uuid4()), definition.id, definition.version, ExerciseStatus.CREATED, QualityStatus.UNKNOWN)
    output.status = ExerciseStatus.RUNNING
    required_failed: list[str] = []
    optional_unavailable: list[str] = []
    for child_id in (*definition.required_children, *definition.optional_children):
        try:
            run = child_runner(child_id)
        except Exception as exc:
            if child_id in definition.required_children:
                required_failed.append(child_id)
            else:
                optional_unavailable.append(child_id)
            continue
        output.child_runs[child_id] = run
        if run.status in {ExerciseStatus.BLOCKED, ExerciseStatus.FAILED}:
            (required_failed if child_id in definition.required_children else optional_unavailable).append(child_id)
    output.conflicts = _collect_conflicts(output.child_runs)
    if required_failed:
        output.status = ExerciseStatus.BLOCKED
        output.quality_status = QualityStatus.BLOCK
        output.error = f"Required child exercises unavailable: {', '.join(required_failed)}"
        return output
    output.result = _synthesize(definition, output.child_runs, output.conflicts)
    from .visualization import resolve_visualizations
    output.result.visualization_specs = resolve_visualizations(definition.id, output.result, child_runs=output.child_runs)
    output.quality_status = QualityStatus.WARNING if (output.conflicts or optional_unavailable or output.result.data_quality.get("status") == QualityStatus.WARNING.value) else QualityStatus.PASS
    output.status = ExerciseStatus.PARTIAL if optional_unavailable else ExerciseStatus.COMPLETED
    return output


# STR-004 policy: market context and finance are decision-critical. Opportunity,
# HCP and trade signals enrich the strategy but may be unavailable without
# invalidating the validated core evidence. EXE-018 is the synthesis node, not
# a separately executed analytics engine.
STR_004 = CompositeDefinition(
    id="STR-004", version="1.0", name="Brand Growth Strategy",
    required_children=("MKT-003", "MKT-004", "MKT-010", "FIN-008"),
    optional_children=("MKT-011", "SAL-012", "HCP-015", "TRD-019"),
    synthesis_node="EXE-018",
)
