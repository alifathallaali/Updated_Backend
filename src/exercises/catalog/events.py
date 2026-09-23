from __future__ import annotations
from ..schemas import ExerciseDefinition
from ..types import ExerciseType

def _make(exercise_id, name, exercise_type, question, domain, engine, *, required=("period",), optional=(), primary=("VIZ-002",), secondary=("VIZ-003",)):
    return ExerciseDefinition(id=exercise_id, version="1.0", domain=domain, name=name, description=question, type=exercise_type, business_question=question, user_roles=("commercial_manager","brand_manager","sales_manager","medical_manager","executive"), use_cases=("planning","business_review","decision_support"), required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(), time_grain="month", minimum_period=1, methodology=f"Resolve to existing PharmaLens {engine} capabilities only after semantic verification; catalog metadata does not imply a verified binding.", metrics=(), engines=(engine,), minimum_data={"minimum_periods":1}, validation_rules=("required inputs must be available",), primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL")

EVENT_EXERCISE_DEFINITIONS = (
    _make("EVT-001", 'Event Portfolio Review', ExerciseType.REVIEW, 'What scientific and commercial events are represented in the available event portfolio?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-002", 'Event Calendar Intelligence', ExerciseType.DESCRIPTIVE, 'What upcoming and historical events are visible by date and category?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-003", 'Event Budget Review', ExerciseType.REVIEW, 'How is event budget represented across activities?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-004", 'Event Attendance Review', ExerciseType.REVIEW, 'What attendance evidence is available across events?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-005", 'Event HCP Reach', ExerciseType.REVIEW, 'What HCP reach is represented by available event data?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-006", 'Event Engagement Review', ExerciseType.REVIEW, 'What engagement signals are available for events?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-007", 'Event Cost per Attendee', ExerciseType.DIAGNOSTIC, 'What cost-per-attendee evidence can be calculated from available inputs?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-008", 'Event Cost per HCP', ExerciseType.DIAGNOSTIC, 'What cost-per-HCP evidence is supported by available inputs?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-009", 'Event Geographic Coverage', ExerciseType.DESCRIPTIVE, 'How are events distributed geographically?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-010", 'Event Therapeutic Coverage', ExerciseType.DESCRIPTIVE, 'How are events distributed across therapeutic areas?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-011", 'Event Type Mix', ExerciseType.DESCRIPTIVE, 'What is the mix of event types in the available portfolio?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-012", 'Event Outcome Review', ExerciseType.REVIEW, 'What observed outcomes are linked to completed events?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-013", 'Event ROI Evidence Review', ExerciseType.REVIEW, 'What ROI evidence is available without unsupported attribution?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-014", 'Event Opportunity Calendar', ExerciseType.OPPORTUNITY, 'What upcoming event opportunities are visible from available sources?', 'Events & Activities Intelligence', 'events'),
    _make("EVT-015", 'Event Portfolio Planning', ExerciseType.PLANNING, 'What event-planning options are supported by budget, coverage and timing evidence?', 'Events & Activities Intelligence', 'events'),
)
