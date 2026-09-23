from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from .types import DataAvailabilityStatus, ExerciseStatus, ExerciseType, QualityStatus

@dataclass(frozen=True)
class ExerciseDefinition:
    id: str
    version: str
    domain: str
    name: str
    description: str
    type: ExerciseType
    status: str = "ACTIVE"
    business_question: str = ""
    user_roles: tuple[str, ...] = ()
    use_cases: tuple[str, ...] = ()
    frequency: str = "ad_hoc"
    decision_context: str = ""
    required_inputs: tuple[str, ...] = ()
    optional_inputs: tuple[str, ...] = ()
    dimensions: tuple[str, ...] = ()
    measures: tuple[str, ...] = ()
    time_grain: str = "month"
    minimum_period: int = 2
    methodology: str = ""
    metrics: tuple[str, ...] = ()
    engines: tuple[str, ...] = ()
    minimum_data: dict[str, Any] = field(default_factory=dict)
    validation_rules: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    primary_visualizations: tuple[str, ...] = ()
    secondary_visualizations: tuple[str, ...] = ()
    allowed_roles: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    data_classification: str = "INTERNAL"
    lineage_source: str = "canonical_data"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class DataAvailability:
    status: DataAvailabilityStatus
    required_columns: tuple[str, ...]
    available_columns: tuple[str, ...]
    missing_columns: tuple[str, ...] = ()
    coverage_pct: float = 0.0
    warnings: tuple[str, ...] = ()

@dataclass
class CanonicalResult:
    executive_summary: str
    key_findings: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    drivers: list[dict[str, Any]] = field(default_factory=list)
    risks: list[dict[str, Any]] = field(default_factory=list)
    opportunities: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    expected_impact: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    lineage: dict[str, Any] = field(default_factory=dict)
    visualization_specs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class ExerciseRun:
    run_id: str
    exercise_id: str
    exercise_version: str
    status: ExerciseStatus
    quality_status: QualityStatus
    created_at: str
    user_id: str | None
    organization_id: str | None
    market: str | None
    data_snapshot: str | None
    engine_versions: dict[str, str]
    parameters: dict[str, Any]
    result: CanonicalResult | None = None
    data_availability: DataAvailability | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
