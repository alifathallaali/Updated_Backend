from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","sales_manager","medical_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

EXECUTIVE_EXERCISE_DEFINITIONS = (
    _make("EXE-001", 'Executive KPI Review', ExerciseType.REVIEW, 'What are the current executive-level commercial KPIs?', 'Executive Intelligence', 'company'),
    _make("EXE-002", 'Business Performance Review', ExerciseType.REVIEW, 'What business-performance signals require executive attention?', 'Executive Intelligence', 'company'),
    _make("EXE-003", 'Market and Brand Review', ExerciseType.REVIEW, 'How are market and brand performance evolving?', 'Executive Intelligence', 'company'),
    _make("EXE-004", 'Portfolio Performance Review', ExerciseType.REVIEW, 'How is the portfolio performing across key commercial measures?', 'Executive Intelligence', 'company'),
    _make("EXE-005", 'Forecast and Outlook Review', ExerciseType.REVIEW, 'What forecast and outlook evidence is currently available?', 'Executive Intelligence', 'company'),
    _make("EXE-006", 'Budget and Financial Review', ExerciseType.REVIEW, 'What budget and financial signals are visible?', 'Executive Intelligence', 'company'),
    _make("EXE-007", 'Launch Portfolio Review', ExerciseType.REVIEW, 'What is the status of active and planned launches?', 'Executive Intelligence', 'company'),
    _make("EXE-008", 'Market Access Review', ExerciseType.REVIEW, 'What market-access signals and risks require review?', 'Executive Intelligence', 'company'),
    _make("EXE-009", 'Field Force Review', ExerciseType.REVIEW, 'What field-force performance and coverage signals are visible?', 'Executive Intelligence', 'company'),
    _make("EXE-010", 'Customer Opportunity Review', ExerciseType.OPPORTUNITY, 'What customer opportunities are supported by available evidence?', 'Executive Intelligence', 'company'),
    _make("EXE-011", 'Commercial Risk Review', ExerciseType.REVIEW, 'What commercial risks are currently documented or detected?', 'Executive Intelligence', 'company'),
    _make("EXE-012", 'Strategic Initiative Review', ExerciseType.REVIEW, 'What is the status of strategic initiatives and their documented outcomes?', 'Executive Intelligence', 'company'),
    _make("EXE-013", 'Decision and Action Review', ExerciseType.REVIEW, 'What open decisions, actions and owners require executive follow-up?', 'Executive Intelligence', 'company'),
    _make("EXE-014", 'Scenario Review', ExerciseType.SCENARIO, 'How do current strategic scenarios compare under stated assumptions?', 'Executive Intelligence', 'company'),
    _make("EXE-015", 'Executive Business Review', ExerciseType.COMPOSITE, 'What integrated evidence should be presented for the executive business review?', 'Executive Intelligence', 'company'),
)
