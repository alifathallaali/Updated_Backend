"""Canonical Sales exercise catalog.

Definitions are metadata only. Registration does not imply that an execution
binding is verified; the runner/semantic-verification layers remain authoritative.
"""
from __future__ import annotations

from ..schemas import ExerciseDefinition
from ..types import ExerciseType


def _sales(exercise_id: str, name: str, exercise_type: ExerciseType, question: str, *, metrics=(), engines=(), required=("period", "sales_value"), optional=()) -> ExerciseDefinition:
    return ExerciseDefinition(
        id=exercise_id,
        version="1.0",
        domain="Sales Intelligence & Performance",
        name=name,
        description=question,
        type=exercise_type,
        business_question=question,
        user_roles=("sales_manager", "commercial_manager", "brand_manager", "executive"),
        use_cases=("performance_review", "business_review", "commercial_planning"),
        required_inputs=tuple(required),
        optional_inputs=tuple(optional),
        dimensions=("period",),
        measures=("sales_value",),
        time_grain="month",
        minimum_period=2,
        methodology="Resolve to an existing verified PharmaLens capability; calculations remain deterministic and governed by the runner.",
        metrics=tuple(metrics),
        engines=tuple(engines),
        minimum_data={"minimum_periods": 2},
        validation_rules=("required inputs must be available", "numeric measures must be valid"),
        primary_visualizations=("VIZ-003",),
        secondary_visualizations=("VIZ-001",),
        data_classification="INTERNAL",
    )


SALES_EXERCISE_DEFINITIONS = (
    _sales("SAL-001", "Sales Performance", ExerciseType.DESCRIPTIVE, "How is sales performance evolving?"),
    _sales("SAL-002", "Actual vs Target", ExerciseType.DIAGNOSTIC, "How is actual sales performance tracking against target?", required=("period", "sales_value", "target")),
    _sales("SAL-003", "Growth Analysis", ExerciseType.DESCRIPTIVE, "How has sales growth changed over time?"),
    _sales("SAL-004", "Contribution Analysis", ExerciseType.DIAGNOSTIC, "Which entities contribute to total sales performance?"),
    _sales("SAL-005", "Mix Analysis", ExerciseType.DESCRIPTIVE, "How is the sales mix distributed across relevant dimensions?"),
    _sales("SAL-006", "Growth Decomposition", ExerciseType.DIAGNOSTIC, "What components explain observed sales growth?"),
    _sales("SAL-007", "Price Volume Analysis", ExerciseType.DIAGNOSTIC, "How do price and volume contribute to sales change?", required=("period", "sales_value", "sales_units"), optional=("selling_price",)),
    _sales("SAL-008", "Sales Decline Diagnosis", ExerciseType.DIAGNOSTIC, "Why did sales decline?", optional=("brand", "product", "target", "price", "volume", "territory", "customer", "competition", "distribution"), metrics=("sales_start", "sales_end", "sales_growth_pct"), engines=("sales_trend_capability",)),
    _sales("SAL-009", "Sales Growth Driver", ExerciseType.DIAGNOSTIC, "What factors are associated with sales growth?"),
    _sales("SAL-010", "Lost Sales Analysis", ExerciseType.DIAGNOSTIC, "Where is lost sales concentrated?"),
    _sales("SAL-011", "Customer Gain Loss", ExerciseType.DIAGNOSTIC, "Which customers account for gains and losses?", optional=("customer",)),
    _sales("SAL-012", "Brand Growth Driver", ExerciseType.DIAGNOSTIC, "What evidence explains brand growth performance?", optional=("brand",)),
    _sales("SAL-013", "Territory Growth Driver", ExerciseType.DIAGNOSTIC, "What evidence explains territory growth performance?", optional=("territory",)),
    _sales("SAL-014", "Rep Growth Driver", ExerciseType.DIAGNOSTIC, "What evidence explains representative-level growth performance?", optional=("rep",)),
    _sales("SAL-015", "Sales Forecast", ExerciseType.PREDICTIVE, "What is the governed sales forecast for the selected scope?"),
)
