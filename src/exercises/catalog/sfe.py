"""Canonical Sales Force Effectiveness (SFE) exercise catalog.

Metadata definitions only. Registration does not imply an execution binding is
verified; semantic verification and the governed runner remain authoritative.
"""
from __future__ import annotations

from ..schemas import ExerciseDefinition
from ..types import ExerciseType


def _sfe(
    exercise_id: str,
    name: str,
    exercise_type: ExerciseType,
    question: str,
    *,
    required=("period",),
    optional=(),
    metrics=(),
    engines=(),
    primary=("VIZ-005",),
    secondary=("VIZ-001",),
) -> ExerciseDefinition:
    return ExerciseDefinition(
        id=exercise_id,
        version="1.0",
        domain="Sales Force Effectiveness",
        name=name,
        description=question,
        type=exercise_type,
        business_question=question,
        user_roles=("sales_manager", "sfe_manager", "commercial_manager", "executive"),
        use_cases=("field_force_review", "territory_review", "commercial_planning"),
        required_inputs=tuple(required),
        optional_inputs=tuple(optional),
        dimensions=("period",),
        measures=(),
        time_grain="month",
        minimum_period=1,
        methodology="Resolve to an existing verified PharmaLens capability; calculations remain deterministic and governed by the runner.",
        metrics=tuple(metrics),
        engines=tuple(engines),
        minimum_data={"minimum_periods": 1},
        validation_rules=("required inputs must be available",),
        primary_visualizations=tuple(primary),
        secondary_visualizations=tuple(secondary),
        data_classification="INTERNAL",
    )


SFE_EXERCISE_DEFINITIONS = (
    _sfe("SFE-001", "Territory Performance", ExerciseType.DESCRIPTIVE, "How are territories performing?", optional=("territory", "sales_value", "target")),
    _sfe("SFE-002", "Rep Performance", ExerciseType.DESCRIPTIVE, "How are field representatives performing?", optional=("rep", "territory", "sales_value", "target")),
    _sfe("SFE-003", "Call Activity", ExerciseType.MONITORING, "What field-call activity is being delivered?", optional=("rep", "hcp", "calls")),
    _sfe("SFE-004", "Reach & Frequency", ExerciseType.DIAGNOSTIC, "Are priority customers receiving the intended reach and frequency?", optional=("hcp", "segment", "calls", "frequency")),
    _sfe("SFE-005", "Coverage Analysis", ExerciseType.DIAGNOSTIC, "Where are field-force coverage gaps concentrated?", optional=("territory", "hcp", "segment", "calls"), primary=("VIZ-013",)),
    _sfe("SFE-006", "Customer Targeting", ExerciseType.DECISION_SUPPORT, "Which customers should be prioritized using available evidence?", optional=("hcp", "segment", "potential", "calls"), primary=("VIZ-014",)),
    _sfe("SFE-007", "Customer Segmentation", ExerciseType.DIAGNOSTIC, "How should customers be segmented using governed criteria?", optional=("hcp", "potential", "specialty", "behavior"), primary=("VIZ-014",)),
    _sfe("SFE-008", "Rep Productivity", ExerciseType.DIAGNOSTIC, "How productive is field activity relative to available outputs?", optional=("rep", "calls", "sales_value", "working_days")),
    _sfe("SFE-009", "Workload Analysis", ExerciseType.DIAGNOSTIC, "How is workload distributed across representatives and territories?", optional=("rep", "territory", "hcp", "calls")),
    _sfe("SFE-010", "Field Capacity", ExerciseType.DIAGNOSTIC, "Is current field capacity aligned with workload and opportunity?", optional=("rep", "territory", "workload", "potential")),
    _sfe("SFE-011", "Territory Balance", ExerciseType.DIAGNOSTIC, "Are territories balanced by workload and opportunity?", optional=("territory", "workload", "potential", "sales_value"), primary=("VIZ-013",)),
    _sfe("SFE-012", "Call Plan Adherence", ExerciseType.MONITORING, "How closely does actual activity follow the approved call plan?", optional=("rep", "hcp", "planned_calls", "actual_calls")),
    _sfe("SFE-013", "Frequency Optimization", ExerciseType.OPTIMIZATION, "What visit-frequency allocation best fits the available constraints and priorities?", optional=("hcp", "segment", "frequency", "capacity"), primary=("VIZ-020",)),
    _sfe("SFE-014", "Call Effectiveness", ExerciseType.DIAGNOSTIC, "What evidence is associated with effective field calls?", optional=("rep", "hcp", "calls", "sales_value", "engagement")),
    _sfe("SFE-015", "Field Force Sizing", ExerciseType.OPTIMIZATION, "What field-force size is supported by workload, coverage and constraints?", optional=("territory", "workload", "capacity", "budget"), primary=("VIZ-020",)),
    _sfe("SFE-016", "Territory Alignment", ExerciseType.OPTIMIZATION, "How could territories be aligned under the defined business constraints?", optional=("territory", "hcp", "potential", "travel", "capacity"), primary=("VIZ-017",)),
    _sfe("SFE-017", "Incentive Performance", ExerciseType.REVIEW, "How is performance tracking against the defined incentive framework?", optional=("rep", "target", "achievement", "incentive")),
    _sfe("SFE-018", "Coaching Opportunity", ExerciseType.OPPORTUNITY, "Where does the evidence indicate field coaching opportunities?", optional=("rep", "kpi", "calls", "achievement")),
    _sfe("SFE-019", "Vacancy Impact", ExerciseType.DIAGNOSTIC, "What observed performance patterns coincide with territory vacancies?", optional=("territory", "vacancy", "sales_value", "calls")),
    _sfe("SFE-020", "SFE Performance Review", ExerciseType.REVIEW, "What does the consolidated SFE evidence show for the selected period?", optional=("rep", "territory", "hcp", "calls", "sales_value", "target"), primary=("VIZ-002",), secondary=("VIZ-003", "VIZ-013")),
)
