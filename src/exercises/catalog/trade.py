from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","sales_manager","medical_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

TRADE_EXERCISE_DEFINITIONS = (
    _make("TRD-001", 'Channel Sales Review', ExerciseType.REVIEW, 'How is commercial performance distributed across channels?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-002", 'Distributor Performance', ExerciseType.REVIEW, 'How are distributors performing across the available commercial measures?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-003", 'Distribution Coverage', ExerciseType.DIAGNOSTIC, 'Where are distribution coverage strengths and gaps visible?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-004", 'Numeric Distribution Review', ExerciseType.REVIEW, 'What numeric distribution evidence is available by product or geography?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-005", 'Weighted Distribution Review', ExerciseType.REVIEW, 'What weighted distribution evidence is available?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-006", 'Stock Availability Review', ExerciseType.MONITORING, 'Where are stock availability issues visible?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-007", 'Stockout Risk Review', ExerciseType.DIAGNOSTIC, 'Where does available evidence indicate stockout risk?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-008", 'Inventory Health Review', ExerciseType.REVIEW, 'What inventory-health signals are visible across channels?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-009", 'Sell-In vs Sell-Out', ExerciseType.DIAGNOSTIC, 'How do sell-in and sell-out patterns compare?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-010", 'Retail Chain Performance', ExerciseType.REVIEW, 'How are retail chains performing across available measures?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-011", 'Pharmacy Segmentation', ExerciseType.DESCRIPTIVE, 'How can pharmacy accounts be described using available commercial attributes?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-012", 'Trade Promotion Review', ExerciseType.REVIEW, 'What evidence is available on trade-promotion activity and outcomes?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-013", 'Channel Mix Analysis', ExerciseType.DIAGNOSTIC, 'How has channel mix changed over time?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-014", 'Regional Distribution Gap', ExerciseType.OPPORTUNITY, 'Where are regional distribution gaps visible?', 'Trade & Distribution', 'market_intelligence'),
    _make("TRD-015", 'Trade Opportunity Review', ExerciseType.OPPORTUNITY, 'What trade opportunities are supported by the available evidence?', 'Trade & Distribution', 'market_intelligence'),
)
