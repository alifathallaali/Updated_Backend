from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","business_development","market_access","finance_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

PORTFOLIO_EXERCISE_DEFINITIONS = (
    _make("PRT-001", 'Portfolio Performance Overview', ExerciseType.DESCRIPTIVE, 'How is the portfolio performing across brands and periods?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-002", 'Portfolio Growth Contribution', ExerciseType.DIAGNOSTIC, 'Which portfolio components contribute to observed growth?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-003", 'Portfolio Mix Analysis', ExerciseType.DESCRIPTIVE, 'How is value distributed across the portfolio?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-004", 'Portfolio Concentration Risk', ExerciseType.DIAGNOSTIC, 'Where is portfolio concentration visible?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-005", 'Portfolio Opportunity Map', ExerciseType.OPPORTUNITY, 'Where are portfolio opportunities visible in the evidence?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-006", 'Lifecycle Position Review', ExerciseType.REVIEW, 'What lifecycle positions are represented across the portfolio?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-007", 'Portfolio Gap Analysis', ExerciseType.DIAGNOSTIC, 'Where are therapeutic or commercial portfolio gaps?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-008", 'Cannibalization Review', ExerciseType.DIAGNOSTIC, 'What overlap signals exist across portfolio brands?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-009", 'Portfolio Scenario Analysis', ExerciseType.SCENARIO, 'How do portfolio scenarios compare under stated assumptions?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-010", 'Resource Allocation Options', ExerciseType.DECISION_SUPPORT, 'What resource-allocation options and trade-offs are supported?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-011", 'Portfolio Risk Matrix', ExerciseType.REVIEW, 'What portfolio risks are documented by likelihood and impact inputs?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-012", 'Portfolio Investment Case', ExerciseType.DECISION_SUPPORT, 'What evidence and assumptions define a portfolio investment case?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-013", 'Portfolio Rationalization Review', ExerciseType.REVIEW, 'What evidence supports reviewing portfolio complexity or focus?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-014", 'Therapeutic Area Portfolio Review', ExerciseType.REVIEW, 'How does the portfolio perform within a therapeutic area?', 'Portfolio Strategy', 'portfolio'),
    _make("PRT-015", 'Portfolio Strategic Options', ExerciseType.DECISION_SUPPORT, 'What portfolio strategic options and trade-offs are supported?', 'Portfolio Strategy', 'portfolio'),
)
