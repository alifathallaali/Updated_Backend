"""Canonical Marketing exercise catalog.

Metadata definitions only. Registration does not imply an execution binding is
verified; semantic verification and the governed runner remain authoritative.
"""
from __future__ import annotations

from ..schemas import ExerciseDefinition
from ..types import ExerciseType


def _marketing(
    exercise_id: str,
    name: str,
    exercise_type: ExerciseType,
    question: str,
    *,
    required=("period", "sales_value"),
    optional=(),
    metrics=(),
    engines=(),
    primary=("VIZ-003",),
    secondary=("VIZ-001",),
) -> ExerciseDefinition:
    return ExerciseDefinition(
        id=exercise_id,
        version="1.0",
        domain="Marketing & Brand Intelligence",
        name=name,
        description=question,
        type=exercise_type,
        business_question=question,
        user_roles=("brand_manager", "marketing_manager", "commercial_manager", "executive"),
        use_cases=("market_review", "brand_review", "brand_planning"),
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
        primary_visualizations=tuple(primary),
        secondary_visualizations=tuple(secondary),
        data_classification="INTERNAL",
    )


MARKETING_EXERCISE_DEFINITIONS = (
    _marketing("MKT-001", "Market Size", ExerciseType.DESCRIPTIVE, "How large is the market?"),
    _marketing("MKT-002", "Market Growth", ExerciseType.DESCRIPTIVE, "How fast is the market growing?"),
    _marketing("MKT-003", "Market Share", ExerciseType.DESCRIPTIVE, "What is our market share and how is it changing?", optional=("brand", "manufacturer", "market"), metrics=("market_share",), engines=("market_intelligence",)),
    _marketing("MKT-004", "Brand Performance", ExerciseType.DIAGNOSTIC, "How is my brand performing within its market?", optional=("brand", "market", "competitor"), engines=("market_intelligence",)),
    _marketing("MKT-005", "Brand Positioning", ExerciseType.DIAGNOSTIC, "Where does our brand sit relative to competitors?", optional=("brand", "competitor", "market"), primary=("VIZ-014",)),
    _marketing("MKT-006", "Brand Lifecycle", ExerciseType.DIAGNOSTIC, "What stage of the lifecycle is the brand in and what does the evidence show?", optional=("brand", "product_launch")),
    _marketing("MKT-007", "Market Attractiveness", ExerciseType.OPPORTUNITY, "How attractive is the selected market based on available evidence?", optional=("market",), primary=("VIZ-014",)),
    _marketing("MKT-008", "Segment Attractiveness", ExerciseType.OPPORTUNITY, "Which market segments show attractive opportunity characteristics?", optional=("segment", "market"), primary=("VIZ-014",)),
    _marketing("MKT-009", "Competitor Mapping", ExerciseType.DIAGNOSTIC, "How are competitors positioned across the selected market?", optional=("competitor", "brand", "market"), primary=("VIZ-014",)),
    _marketing("MKT-010", "Competitive Gap", ExerciseType.DIAGNOSTIC, "Where are the measurable competitive gaps?", optional=("manufacturer", "brand", "competitor", "market"), engines=("market_intelligence",)),
    _marketing("MKT-011", "White Space", ExerciseType.OPPORTUNITY, "Where does the available evidence indicate market white space?", optional=("brand", "market", "segment"), primary=("VIZ-014",)),
    _marketing("MKT-012", "Brand Opportunity", ExerciseType.OPPORTUNITY, "Where are the evidence-backed growth opportunities for the brand?", optional=("brand", "market", "segment"), primary=("VIZ-014",)),
    _marketing("MKT-013", "Campaign Performance", ExerciseType.REVIEW, "How did the campaign perform against its defined objectives?", required=("period",), optional=("campaign", "sales_value", "target", "engagement"), primary=("VIZ-005",)),
    _marketing("MKT-014", "Campaign ROI", ExerciseType.DIAGNOSTIC, "What is the governed return on campaign investment?", required=("period", "campaign_cost"), optional=("incremental_value", "sales_value", "campaign"), primary=("VIZ-009",)),
    _marketing("MKT-015", "Brand Plan", ExerciseType.PLANNING, "What evidence and decisions should inform the brand plan?", optional=("brand", "market", "target", "budget"), primary=("VIZ-024",)),
)
