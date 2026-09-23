from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","business_development","market_access","finance_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

MARKET_ACCESS_EXERCISE_DEFINITIONS = (
    _make("MAX-001", 'Access Landscape Review', ExerciseType.DESCRIPTIVE, 'What does the current access landscape show?', 'Market Access', 'market_access'),
    _make("MAX-002", 'Payer Segmentation', ExerciseType.DECISION_SUPPORT, 'How can payers be segmented using available access evidence?', 'Market Access', 'market_access'),
    _make("MAX-003", 'Reimbursement Status Review', ExerciseType.REVIEW, 'What reimbursement status is observed across products or accounts?', 'Market Access', 'market_access'),
    _make("MAX-004", 'Formulary Access Analysis', ExerciseType.DIAGNOSTIC, 'Where is formulary access present or absent?', 'Market Access', 'market_access'),
    _make("MAX-005", 'Access Barrier Analysis', ExerciseType.DIAGNOSTIC, 'What access barriers are documented in the available evidence?', 'Market Access', 'market_access'),
    _make("MAX-006", 'Value Proposition Evidence Map', ExerciseType.REVIEW, 'What evidence supports the value proposition by stakeholder?', 'Market Access', 'market_access'),
    _make("MAX-007", 'Price & Access Scenario', ExerciseType.SCENARIO, 'How do price and access assumptions interact across scenarios?', 'Market Access', 'market_access'),
    _make("MAX-008", 'Budget Impact Review', ExerciseType.DECISION_SUPPORT, 'What budget-impact evidence is available for decision support?', 'Market Access', 'market_access'),
    _make("MAX-009", 'Tender Access Opportunity', ExerciseType.OPPORTUNITY, 'Where are tender-related access opportunities visible?', 'Market Access', 'market_access'),
    _make("MAX-010", 'Hospital Access Mapping', ExerciseType.DESCRIPTIVE, 'How does hospital access vary across the covered accounts?', 'Market Access', 'market_access'),
    _make("MAX-011", 'Payer Evidence Gap', ExerciseType.DIAGNOSTIC, 'What payer evidence gaps limit access decisions?', 'Market Access', 'market_access'),
    _make("MAX-012", 'Access Readiness Assessment', ExerciseType.REVIEW, 'How ready is the available evidence for an access decision?', 'Market Access', 'market_access'),
    _make("MAX-013", 'Contracting Scenario Review', ExerciseType.SCENARIO, 'How do alternative contracting assumptions compare?', 'Market Access', 'market_access'),
    _make("MAX-014", 'Access Action Planning', ExerciseType.PLANNING, 'What access actions follow from validated findings?', 'Market Access', 'market_access'),
    _make("MAX-015", 'Market Access Strategic Review', ExerciseType.DECISION_SUPPORT, 'What access options, risks and trade-offs are supported?', 'Market Access', 'market_access'),
)
