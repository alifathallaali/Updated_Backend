"""Canonical HCP/KOL intelligence exercise catalog.

Metadata only. Existing Medical Affairs capabilities remain authoritative for
scoring/calculation; catalog registration never implies a verified binding.
"""
from __future__ import annotations

from ..schemas import ExerciseDefinition
from ..types import ExerciseType


def _hcp(exercise_id, name, exercise_type, question, *, required=("period",), optional=(), primary=("VIZ-006",), secondary=("VIZ-013",)):
    return ExerciseDefinition(
        id=exercise_id, version="1.0", domain="HCP & KOL Intelligence", name=name,
        description=question, type=exercise_type, business_question=question,
        user_roles=("medical_manager", "medical_affairs", "sales_manager", "sfe_manager", "brand_manager", "commercial_manager"),
        use_cases=("hcp_segmentation", "kol_planning", "engagement_planning", "business_review"),
        required_inputs=tuple(required), optional_inputs=tuple(optional), dimensions=("period",), measures=(),
        time_grain="month", minimum_period=1,
        methodology="Resolve to existing PharmaLens Medical Affairs/HCP capabilities only after semantic verification; deterministic scoring remains in the existing engine.",
        metrics=(), engines=("medical_affairs",), minimum_data={"minimum_periods": 1},
        validation_rules=("required inputs must be available",),
        primary_visualizations=tuple(primary), secondary_visualizations=tuple(secondary), data_classification="INTERNAL",
    )


HCP_KOL_EXERCISE_DEFINITIONS = (
    _hcp("HCP-001", "HCP Universe Profiling", ExerciseType.DESCRIPTIVE, "What does the available HCP universe look like by specialty, geography and account?", optional=("hcp_id", "specialty", "region", "account")),
    _hcp("HCP-002", "HCP Segmentation", ExerciseType.DECISION_SUPPORT, "How can HCPs be segmented using governed commercial and medical evidence?", optional=("hcp_id", "specialty", "potential", "engagement", "rx"), primary=("VIZ-014",)),
    _hcp("HCP-003", "HCP Potential Scoring", ExerciseType.OPPORTUNITY, "What relative HCP potential is supported by the available evidence?", optional=("hcp_id", "rx", "patient_potential", "account_potential")),
    _hcp("HCP-004", "HCP Prioritization", ExerciseType.DECISION_SUPPORT, "Which HCPs fall into priority groups under the approved scoring rules?", optional=("hcp_id", "potential", "engagement", "access"), primary=("VIZ-014",)),
    _hcp("HCP-005", "HCP Engagement Analysis", ExerciseType.DIAGNOSTIC, "How does HCP engagement vary across the available channels and periods?", optional=("hcp_id", "channel", "interaction_count", "engagement_score"), primary=("VIZ-003",)),
    _hcp("HCP-006", "HCP Reach & Frequency", ExerciseType.MONITORING, "What reach and contact frequency are observed across the target HCP universe?", optional=("hcp_id", "calls", "target_flag"), primary=("VIZ-002",)),
    _hcp("HCP-007", "HCP Coverage Gap", ExerciseType.DIAGNOSTIC, "Where are the largest gaps between target HCPs and observed coverage?", optional=("hcp_id", "target_flag", "calls", "region"), primary=("VIZ-013",)),
    _hcp("HCP-008", "HCP Response Analysis", ExerciseType.DIAGNOSTIC, "What response patterns are observed following HCP engagement?", optional=("hcp_id", "engagement", "rx", "sales_value"), primary=("VIZ-011",)),
    _hcp("HCP-009", "HCP Channel Preference", ExerciseType.DESCRIPTIVE, "Which engagement channels are most represented for each HCP segment?", optional=("hcp_id", "channel", "segment", "interaction_count"), primary=("VIZ-008",)),
    _hcp("HCP-010", "KOL Identification", ExerciseType.OPPORTUNITY, "Which HCPs meet the approved evidence criteria for potential KOL consideration?", optional=("hcp_id", "scientific_activity", "network", "engagement")),
    _hcp("HCP-011", "KOL Influence Mapping", ExerciseType.DECISION_SUPPORT, "How does modeled KOL influence compare across the available evidence?", optional=("hcp_id", "influence_score", "network", "scientific_activity"), primary=("VIZ-011",)),
    _hcp("HCP-012", "KOL Engagement Planning", ExerciseType.PLANNING, "How can KOL engagement be organized by objective, evidence and channel?", optional=("hcp_id", "influence_score", "engagement", "objective"), primary=("VIZ-016",)),
    _hcp("HCP-013", "Scientific Engagement Review", ExerciseType.REVIEW, "What does the available evidence show about scientific engagement activity and coverage?", optional=("hcp_id", "activity_type", "interaction_count", "topic"), primary=("VIZ-002",)),
    _hcp("HCP-014", "HCP Opportunity Matrix", ExerciseType.OPPORTUNITY, "Where are HCP opportunities when potential and engagement evidence are considered together?", optional=("hcp_id", "potential", "engagement", "access"), primary=("VIZ-014",)),
    _hcp("HCP-015", "KOL Opportunity Scoring", ExerciseType.OPPORTUNITY, "What KOL opportunity signal is supported by the existing Medical Affairs scoring capability?", optional=("hcp_id", "publications", "trials", "speaking", "guidelines", "influence_score"), primary=("VIZ-014",)),
)
