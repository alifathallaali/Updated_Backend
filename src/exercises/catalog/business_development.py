from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","business_development","market_access","finance_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS = (
    _make("BD-001", 'Market Attractiveness Screening', ExerciseType.OPPORTUNITY, 'Where are commercially attractive growth spaces?', 'Business Development', 'business_development'),
    _make("BD-002", 'Licensing Opportunity Screening', ExerciseType.OPPORTUNITY, 'Which licensing opportunities merit structured assessment?', 'Business Development', 'business_development'),
    _make("BD-003", 'Partner Landscape Mapping', ExerciseType.DESCRIPTIVE, 'What potential partners are visible in the available evidence?', 'Business Development', 'business_development'),
    _make("BD-004", 'Deal Pipeline Review', ExerciseType.REVIEW, 'What is the status and composition of the business-development pipeline?', 'Business Development', 'business_development'),
    _make("BD-005", 'Asset Opportunity Assessment', ExerciseType.DECISION_SUPPORT, 'What commercial opportunity is supported for a candidate asset?', 'Business Development', 'business_development'),
    _make("BD-006", 'New Market Entry Screening', ExerciseType.OPPORTUNITY, 'Which markets merit deeper entry assessment?', 'Business Development', 'business_development'),
    _make("BD-007", 'Commercial Due Diligence', ExerciseType.REVIEW, 'What commercial evidence supports due-diligence review?', 'Business Development', 'business_development'),
    _make("BD-008", 'Revenue Synergy Assessment', ExerciseType.SCENARIO, 'What revenue synergies are supported by the available assumptions and evidence?', 'Business Development', 'business_development'),
    _make("BD-009", 'Portfolio Gap Analysis', ExerciseType.DIAGNOSTIC, 'Where are strategic portfolio gaps visible?', 'Business Development', 'business_development'),
    _make("BD-010", 'Growth White-Space Analysis', ExerciseType.OPPORTUNITY, 'Where are unaddressed commercial growth spaces?', 'Business Development', 'business_development'),
    _make("BD-011", 'Partnership Scenario Analysis', ExerciseType.SCENARIO, 'How do alternative partnership structures compare?', 'Business Development', 'business_development'),
    _make("BD-012", 'Deal Assumption Sensitivity', ExerciseType.SCENARIO, 'Which assumptions most affect the deal case?', 'Business Development', 'business_development'),
    _make("BD-013", 'Business Case Review', ExerciseType.REVIEW, 'What evidence, assumptions and risks define the business case?', 'Business Development', 'business_development'),
    _make("BD-014", 'Opportunity Prioritization', ExerciseType.DECISION_SUPPORT, 'How can opportunities be organized for decision review without unsupported ranking?', 'Business Development', 'business_development'),
    _make("BD-015", 'BD Strategic Options', ExerciseType.DECISION_SUPPORT, 'What strategic business-development options and trade-offs are supported?', 'Business Development', 'business_development'),
    _make("BD-016", 'Line Extension', ExerciseType.OPPORTUNITY, 'What line-extension opportunities are supported by the available commercial evidence?', 'Business Development', 'business_development'),
    _make("BD-017", 'Commercial Feasibility', ExerciseType.DECISION_SUPPORT, 'What commercial feasibility is supported by the available evidence and assumptions?', 'Business Development', 'business_development'),
    _make("BD-018", 'Strategic Fit', ExerciseType.DECISION_SUPPORT, 'How does the opportunity fit the stated strategic context and portfolio?', 'Business Development', 'business_development'),
    _make("BD-019", 'Revenue Opportunity', ExerciseType.OPPORTUNITY, 'What revenue opportunity can be evaluated from validated inputs and existing capabilities?', 'Business Development', 'business_development'),
    _make("BD-020", 'Investment Scenario', ExerciseType.SCENARIO, 'How do alternative investment assumptions change the business-development scenario?', 'Business Development', 'business_development'),
)
