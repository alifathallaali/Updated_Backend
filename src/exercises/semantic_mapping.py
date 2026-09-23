from __future__ import annotations

from dataclasses import dataclass, asdict
import importlib
import inspect
from typing import Any


@dataclass(frozen=True)
class CapabilityCandidate:
    exercise_id: str
    module: str
    callable_name: str
    capability: str
    status: str  # VERIFIED | CANDIDATE | UNMAPPED
    rationale: str
    required_inputs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Candidates are deliberately explicit. They are NOT executable bindings until
# the exercise contract and callable input/output semantics are validated.
CAPABILITY_CANDIDATES: tuple[CapabilityCandidate, ...] = (
    CapabilityCandidate(
        "MKT-003", "src.engines.market_intelligence.market_intelligence",
        "market_share_by_brand", "market_intelligence.market_share_by_brand",
        "VERIFIED", "Exact market-share-by-brand capability already validated.",
        ("Brand Name", "Sales Value"),
    ),
    CapabilityCandidate(
        "MKT-004", "src.engines.market_intelligence.market_intelligence",
        "market_summary", "market_intelligence.market_summary",
        "CANDIDATE", "Market-level summary exists, but the exercise definition must confirm that its output matches MKT-004 semantics.",
        ("Sales Value", "Sales Units"),
    ),
    CapabilityCandidate(
        "MKT-010", "src.engines.market_intelligence.market_intelligence",
        "market_share_by_manufacturer", "market_intelligence.market_share_by_manufacturer",
        "CANDIDATE", "Manufacturer-share capability exists; exercise semantics must be checked before binding.",
        ("Manufacturer", "Sales Value"),
    ),
    CapabilityCandidate(
        "MKT-011", "src.engines.recommendation.recommendation",
        "opportunity_analysis", "recommendation.opportunity_analysis",
        "UNMAPPED", "Existing opportunity_analysis is a pass-through placeholder (returns the input dataframe) and does not implement White Space semantics; keep blocked until a real reusable capability exists.",
        ("Sales Value",),
    ),
    CapabilityCandidate(
        "SAL-012", "src.engines.recommendation.recommendation",
        "opportunity_analysis", "recommendation.opportunity_analysis",
        "UNMAPPED", "Existing opportunity_analysis is a pass-through placeholder and does not implement Sales Opportunity Analysis semantics; keep blocked until a real reusable capability exists.",
        ("Sales Value",),
    ),
    CapabilityCandidate(
        "HCP-015", "src.engines.medical_affairs.medical_affairs_intelligence",
        "score_kols", "medical_affairs.score_kols",
        "VERIFIED", "KOL scoring capability input/output contract validated against HCP-015; score is explicitly modeled, not observed.",
        ("publication_count", "citation_count"),
    ),
    CapabilityCandidate(
        "TRD-019", "src.engines.gtm.gtm",
        "channel_performance", "gtm.channel_performance",
        "CANDIDATE", "Channel performance capability exists; exercise contract must confirm channel-level semantics.",
        ("Distribution Channel", "Sales Value", "Sales Units"),
    ),
    CapabilityCandidate(
        "FIN-008", "src.engines.commercial_finance.commercial_finance",
        "price_volume_analysis", "commercial_finance.price_volume_analysis",
        "VERIFIED", "FIN-008 contract validated: the adapter derives earliest/latest observed period price-volume inputs and delegates decomposition to the existing finance capability.",
        ("Year", "Month", "Selling Price", "Sales Units"),
    ),
    CapabilityCandidate(
        "EXE-018", "", "", "", "UNMAPPED",
        "No existing deterministic capability has been verified for the executive synthesis exercise; it should orchestrate evidence rather than invent a new analytics engine.",
        (),
    ),
)


def candidates_for(exercise_id: str) -> list[CapabilityCandidate]:
    key = exercise_id.upper()
    return [c for c in CAPABILITY_CANDIDATES if c.exercise_id == key]


def inspect_candidate(candidate: CapabilityCandidate) -> dict[str, Any]:
    if not candidate.module or not candidate.callable_name:
        return {**candidate.to_dict(), "import_healthy": False, "callable_healthy": False, "signature": None,
                "runtime_status": "UNMAPPED"}
    try:
        module = importlib.import_module(candidate.module)
        fn = getattr(module, candidate.callable_name)
        return {**candidate.to_dict(), "import_healthy": True, "callable_healthy": callable(fn),
                "signature": str(inspect.signature(fn)),
                "runtime_status": "READY" if callable(fn) else "BLOCKED"}
    except Exception as exc:
        return {**candidate.to_dict(), "import_healthy": False, "callable_healthy": False,
                "signature": None, "runtime_status": "BLOCKED", "error": str(exc)}


def inspect_str_004() -> list[dict[str, Any]]:
    return [inspect_candidate(c) for c in CAPABILITY_CANDIDATES]
