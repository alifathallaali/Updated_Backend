from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","sales_manager","medical_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

STRATEGIC_EXERCISE_DEFINITIONS = (
    _make("STR-001", 'Market Entry Business Case', ExerciseType.COMPOSITE, 'What evidence, assumptions, risks and scenarios define a market-entry business case?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-002", 'Portfolio Investment Allocation', ExerciseType.COMPOSITE, 'What portfolio investment options and trade-offs are supported by available evidence?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-003", 'Field Force Expansion Scenario', ExerciseType.COMPOSITE, 'What field-force expansion scenarios and trade-offs are supported?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-004", 'Brand Growth Strategy', ExerciseType.COMPOSITE, 'What evidence-backed strategic options are available to support brand growth?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-005", 'Therapeutic Area Expansion', ExerciseType.COMPOSITE, 'What evidence supports therapeutic-area expansion options?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-006", 'Launch Investment Decision Support', ExerciseType.COMPOSITE, 'What launch-investment options and trade-offs are supported by available evidence?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-007", 'Licensing Opportunity Assessment', ExerciseType.COMPOSITE, 'What evidence, assumptions and risks define the licensing opportunity?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-008", 'Commercial Turnaround Plan', ExerciseType.COMPOSITE, 'What evidence-backed commercial turnaround options are available?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-009", 'Annual Strategic Plan', ExerciseType.COMPOSITE, 'What evidence, priorities, scenarios and actions define the annual strategic plan?', 'Strategic Decision Support', 'exercise_orchestrator'),
    _make("STR-010", '3-Year Commercial Scenario', ExerciseType.COMPOSITE, 'How do base, growth, defensive and custom three-year commercial scenarios compare under stated assumptions?', 'Strategic Decision Support', 'exercise_orchestrator'),
)
