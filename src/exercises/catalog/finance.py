from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","business_development","market_access","finance_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

FINANCE_EXERCISE_DEFINITIONS = (
    _make("FIN-001", 'Revenue Performance', ExerciseType.DESCRIPTIVE, 'How has revenue performed over the selected period?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-002", 'Gross Margin Review', ExerciseType.REVIEW, 'What gross-margin performance is supported by available finance data?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-003", 'Budget vs Actual', ExerciseType.DIAGNOSTIC, 'How do actual results compare with budget?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-004", 'Forecast vs Actual', ExerciseType.DIAGNOSTIC, 'How do actual results compare with the approved forecast?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-005", 'Price Analysis', ExerciseType.DIAGNOSTIC, 'How have realized prices changed across periods or segments?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-006", 'Volume Analysis', ExerciseType.DIAGNOSTIC, 'How have volumes changed across periods or segments?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-007", 'Mix Analysis', ExerciseType.DIAGNOSTIC, 'What mix shifts are visible in commercial performance?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-008", 'Price Volume Analysis', ExerciseType.DIAGNOSTIC, 'How much of observed change is represented by price and volume components?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-009", 'Profitability Review', ExerciseType.REVIEW, 'What profitability evidence is available by product or segment?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-010", 'Contribution Margin Analysis', ExerciseType.DIAGNOSTIC, 'What contribution-margin evidence is available?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-011", 'Commercial ROI Review', ExerciseType.REVIEW, 'What ROI evidence is available for commercial investments?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-012", 'Budget Allocation Scenario', ExerciseType.SCENARIO, 'How do alternative budget allocations compare under stated assumptions?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-013", 'Reforecast Review', ExerciseType.REVIEW, 'What changes are reflected in the latest reforecast?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-014", 'FX Impact Review', ExerciseType.DIAGNOSTIC, 'What FX-related impact is represented in the available financial inputs?', 'Commercial Finance', 'commercial_finance'),
    _make("FIN-015", 'Incentive Cost Review', ExerciseType.REVIEW, 'What incentive-cost patterns are visible in the available data?', 'Commercial Finance', 'commercial_finance'),
)
