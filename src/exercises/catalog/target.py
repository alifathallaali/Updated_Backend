"""Canonical Smart Target Planning exercise catalog.

Metadata only. The existing target_planning engine remains authoritative for
calculations; registration here does not imply a verified execution binding.
"""
from __future__ import annotations

from ..schemas import ExerciseDefinition
from ..types import ExerciseType


def _target(exercise_id, name, exercise_type, question, *, required=("period",), optional=(), primary=("VIZ-018",), secondary=("VIZ-005",)):
    return ExerciseDefinition(
        id=exercise_id, version="1.0", domain="Smart Target Planning", name=name,
        description=question, type=exercise_type, business_question=question,
        user_roles=("sales_manager", "sfe_manager", "commercial_manager", "brand_manager", "executive"),
        use_cases=("target_setting", "annual_planning", "business_review"),
        required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(),
        time_grain="year", minimum_period=1,
        methodology="Resolve to the existing PharmaLens Smart Target Planning capability after semantic verification; deterministic target calculations remain in the target engine.",
        metrics=(), engines=("target_planning",), minimum_data={"minimum_periods": 1},
        validation_rules=("required inputs must be available",),
        primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL",
    )


TARGET_EXERCISE_DEFINITIONS = (
    _target("TGT-001", "Company Baseline", ExerciseType.DESCRIPTIVE, "What is the governed company sales baseline for target planning?", optional=("sales_units", "sales_value", "year"), primary=("VIZ-002",)),
    _target("TGT-002", "Company Target Setting", ExerciseType.PLANNING, "What company target follows the approved objective and assumptions?", optional=("sales_units", "sales_value", "base_year", "target_year", "growth_rate")),
    _target("TGT-003", "Product Baseline", ExerciseType.DESCRIPTIVE, "What is the product-level baseline for target planning?", optional=("brand", "therapeutic_class", "sales_units", "sales_value", "year"), primary=("VIZ-006",)),
    _target("TGT-004", "Product Target Setting", ExerciseType.PLANNING, "How should product targets be derived from baseline and governed growth assumptions?", optional=("brand", "therapeutic_class", "sales_units", "sales_value", "growth_rate")),
    _target("TGT-005", "Regional Opportunity", ExerciseType.OPPORTUNITY, "How does regional opportunity compare using the available RX, growth and execution evidence?", optional=("region", "rx_potential", "rx_growth", "execution_strength"), primary=("VIZ-013",)),
    _target("TGT-006", "Top-Down Allocation", ExerciseType.PLANNING, "How should an approved company target be allocated across regions by governed opportunity weights?", optional=("region", "opportunity_score", "target_units", "target_value")),
    _target("TGT-007", "Bottom-Up Target Consolidation", ExerciseType.PLANNING, "What company target results from consolidating regional targets?", optional=("region", "target_units", "target_value"), primary=("VIZ-002",)),
    _target("TGT-008", "Target Reconciliation", ExerciseType.OPTIMIZATION, "How can regional targets be reconciled to the approved company target within tolerance?", optional=("region", "target_units", "target_value", "company_target"), primary=("VIZ-020",)),
    _target("TGT-009", "Target Growth Analysis", ExerciseType.DIAGNOSTIC, "How do proposed targets compare with historical growth and baseline performance?", optional=("brand", "region", "historical_growth", "target_growth"), primary=("VIZ-003",)),
    _target("TGT-010", "Target Achievement", ExerciseType.MONITORING, "How is actual performance tracking against target?", optional=("brand", "region", "sales_value", "target_value", "achievement"), primary=("VIZ-018",)),
    _target("TGT-011", "Target Gap Analysis", ExerciseType.DIAGNOSTIC, "Where are the largest gaps between actual performance and target?", optional=("brand", "region", "sales_value", "target_value"), primary=("VIZ-009",)),
    _target("TGT-012", "Target Scenario", ExerciseType.SCENARIO, "How do target allocations change under alternative approved assumptions?", optional=("growth_rate", "damping", "region", "opportunity_score"), primary=("VIZ-019",)),
    _target("TGT-013", "Target Explainability", ExerciseType.REVIEW, "What evidence and assumptions explain each target allocation?", optional=("region", "opportunity_score", "rx_growth", "rx_potential"), primary=("VIZ-022",)),
    _target("TGT-014", "Target Planning Review", ExerciseType.REVIEW, "What does the consolidated target-planning evidence show for the planning cycle?", optional=("region", "brand", "target_units", "target_value", "achievement"), primary=("VIZ-002",), secondary=("VIZ-018", "VIZ-013")),
)
