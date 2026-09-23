from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","sales_manager","medical_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

MEDICAL_EXERCISE_DEFINITIONS = (
    _make("MED-001", 'KOL Landscape', ExerciseType.DESCRIPTIVE, 'What KOL landscape is represented in the available medical-affairs data?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-002", 'KOL Segmentation', ExerciseType.DESCRIPTIVE, 'How can KOLs be segmented using available attributes and modeled scores?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-003", 'KOL Influence Review', ExerciseType.REVIEW, 'What influence signals are available for KOLs?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-004", 'Scientific Engagement Review', ExerciseType.REVIEW, 'What scientific-engagement activity is represented in the available data?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-005", 'Medical Activity Review', ExerciseType.REVIEW, 'What medical-affairs activities occurred over the selected period?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-006", 'Scientific Meeting Review', ExerciseType.REVIEW, 'What evidence is available for scientific meetings and their reach?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-007", 'Advisory Board Review', ExerciseType.REVIEW, 'What advisory-board activity and outputs are documented?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-008", 'Medical Education Review', ExerciseType.REVIEW, 'What medical-education activities and reach are documented?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-009", 'Evidence Gap Mapping', ExerciseType.DIAGNOSTIC, 'Where are evidence gaps visible for the selected medical question?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-010", 'Publication Landscape', ExerciseType.DESCRIPTIVE, 'What publication landscape is represented by available evidence?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-011", 'Investigator Landscape', ExerciseType.DESCRIPTIVE, 'What investigator landscape is represented in the available data?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-012", 'Medical Insight Themes', ExerciseType.DIAGNOSTIC, 'What recurring medical-insight themes are supported by captured evidence?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-013", 'Medical Engagement Coverage', ExerciseType.DIAGNOSTIC, 'Where are medical-engagement coverage gaps visible?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-014", 'Medical Activity Planning', ExerciseType.PLANNING, 'What medical-activity plan is supported by priorities, evidence gaps and constraints?', 'Medical Affairs', 'medical_affairs'),
    _make("MED-015", 'Medical Impact Review', ExerciseType.REVIEW, 'What observed medical-affairs outcomes are available without unsupported causal claims?', 'Medical Affairs', 'medical_affairs'),
)
