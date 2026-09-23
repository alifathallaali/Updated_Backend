from __future__ import annotations
from .schemas import ExerciseDefinition
from .types import ExerciseType
from .definitions_str004 import STR_004_CHILD_DEFINITIONS
from .catalog import SALES_EXERCISE_DEFINITIONS, MARKETING_EXERCISE_DEFINITIONS, SFE_EXERCISE_DEFINITIONS, TARGET_EXERCISE_DEFINITIONS, HCP_KOL_EXERCISE_DEFINITIONS, BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS, MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS, PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS, TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS, MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS, STRATEGIC_EXERCISE_DEFINITIONS

class ExerciseRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ExerciseDefinition] = {}

    def register(self, definition: ExerciseDefinition) -> ExerciseDefinition:
        key = definition.id.upper()
        if key in self._items:
            raise ValueError(f"Exercise already registered: {key}")
        self._items[key] = definition
        return definition

    def upsert(self, definition: ExerciseDefinition) -> ExerciseDefinition:
        self._items[definition.id.upper()] = definition
        return definition

    def get(self, exercise_id: str) -> ExerciseDefinition:
        try:
            return self._items[exercise_id.upper()]
        except KeyError as exc:
            raise KeyError(f"Unknown exercise: {exercise_id}") from exc

    def list(self) -> list[ExerciseDefinition]:
        return list(self._items.values())

registry = ExerciseRegistry()

registry.register(ExerciseDefinition(
    id="SAL-008",
    version="1.0",
    domain="Sales Intelligence & Performance",
    name="Sales Trend & Performance",
    description="Measure sales value trend over the available periods and surface a deterministic performance signal.",
    type=ExerciseType.DIAGNOSTIC,
    business_question="How has sales value changed over the available period?",
    user_roles=("sales_manager", "commercial_manager", "brand_manager", "executive"),
    use_cases=("performance_review", "business_review", "commercial_turnaround"),
    required_inputs=("period", "sales_value"),
    dimensions=("period",),
    measures=("sales_value",),
    time_grain="month",
    minimum_period=2,
    methodology="Sort available periods, aggregate sales value by period, then calculate first-to-last growth deterministically.",
    metrics=("sales_start", "sales_end", "sales_growth_pct"),
    engines=("sales_trend_capability",),
    minimum_data={"minimum_periods": 2},
    validation_rules=("period must contain at least two valid observations", "sales_value must be numeric"),
    primary_visualizations=("VIZ-003",),
    secondary_visualizations=("VIZ-001",),
    data_classification="INTERNAL",
))

for _definition in SALES_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in MARKETING_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in SFE_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in TARGET_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in HCP_KOL_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in MARKET_ACCESS_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in LAUNCH_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in PORTFOLIO_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definition in FINANCE_EXERCISE_DEFINITIONS:
    registry.upsert(_definition)

for _definitions in (TRADE_EXERCISE_DEFINITIONS, EVENT_EXERCISE_DEFINITIONS, MEDICAL_EXERCISE_DEFINITIONS, EXECUTIVE_EXERCISE_DEFINITIONS, STRATEGIC_EXERCISE_DEFINITIONS):
    for _definition in _definitions:
        registry.upsert(_definition)



for _definition in STR_004_CHILD_DEFINITIONS:
    if _definition.id.upper() not in {d.id.upper() for d in registry.list()}:
        registry.register(_definition)
