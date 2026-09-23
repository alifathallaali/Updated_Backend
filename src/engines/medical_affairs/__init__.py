"""Medical Affairs deterministic engine exports.

Agent/tool integrations are optional and must not prevent deterministic analytics
from importing in environments where the legacy agent package is absent.
"""
from .medical_affairs_intelligence import (
    score_kols,
    scientific_landscape,
    publication_intelligence,
    clinical_trial_landscape,
    competitor_pipeline,
    evidence_landscape,
    medical_education_opportunities,
    advisory_board_plan,
    medical_commercial_opportunities,
)

__all__ = [
    "score_kols", "scientific_landscape", "publication_intelligence",
    "clinical_trial_landscape", "competitor_pipeline", "evidence_landscape",
    "medical_education_opportunities", "advisory_board_plan",
    "medical_commercial_opportunities",
]
