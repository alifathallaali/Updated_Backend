from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","business_development","market_access","finance_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

LAUNCH_EXERCISE_DEFINITIONS = (
    _make("LCH-001", 'Launch Readiness Assessment', ExerciseType.REVIEW, 'How ready is the brand for launch across required workstreams?', 'Launch Excellence', 'launch'),
    _make("LCH-002", 'Launch Market Assessment', ExerciseType.DESCRIPTIVE, 'What market context should inform launch planning?', 'Launch Excellence', 'launch'),
    _make("LCH-003", 'Launch Opportunity Sizing', ExerciseType.OPPORTUNITY, 'What launch opportunity is supported by available evidence?', 'Launch Excellence', 'launch'),
    _make("LCH-004", 'Launch Target Customer Definition', ExerciseType.DECISION_SUPPORT, 'Which customer groups are relevant to the launch plan?', 'Launch Excellence', 'launch'),
    _make("LCH-005", 'Launch Forecast Review', ExerciseType.PREDICTIVE, 'What does the existing forecast indicate for launch scenarios?', 'Launch Excellence', 'launch'),
    _make("LCH-006", 'Launch Assumption Review', ExerciseType.REVIEW, 'Which assumptions drive the launch case?', 'Launch Excellence', 'launch'),
    _make("LCH-007", 'Launch Risk Assessment', ExerciseType.DIAGNOSTIC, 'What launch risks are documented and how are they distributed?', 'Launch Excellence', 'launch'),
    _make("LCH-008", 'Launch Milestone Tracking', ExerciseType.MONITORING, 'What is the status of launch milestones?', 'Launch Excellence', 'launch'),
    _make("LCH-009", 'Launch KPI Framework', ExerciseType.PLANNING, 'Which validated KPIs should be monitored for launch execution?', 'Launch Excellence', 'launch'),
    _make("LCH-010", 'Launch Channel Planning', ExerciseType.PLANNING, 'How should launch channels be organized around objectives and evidence?', 'Launch Excellence', 'launch'),
    _make("LCH-011", 'Launch Field Force Readiness', ExerciseType.REVIEW, 'What evidence describes field-force readiness for launch?', 'Launch Excellence', 'launch'),
    _make("LCH-012", 'Launch Access Readiness', ExerciseType.REVIEW, 'What evidence describes market-access readiness for launch?', 'Launch Excellence', 'launch'),
    _make("LCH-013", 'Launch Scenario Comparison', ExerciseType.SCENARIO, 'How do launch scenarios compare under stated assumptions?', 'Launch Excellence', 'launch'),
    _make("LCH-014", 'Post-Launch Performance Review', ExerciseType.REVIEW, 'How is post-launch performance tracking against the available baseline?', 'Launch Excellence', 'launch'),
    _make("LCH-015", 'Launch Optimization Actions', ExerciseType.DECISION_SUPPORT, 'What actions follow from validated launch findings?', 'Launch Excellence', 'launch'),
)
