from __future__ import annotations

from .schemas import ExerciseDefinition
from .types import ExerciseType

# Canonical contracts for the STR-004 child exercises. These definitions are
# intentionally conservative: they describe the minimum semantics needed to
# validate an existing capability and do not invent missing engine behavior.
STR_004_CHILD_DEFINITIONS: tuple[ExerciseDefinition, ...] = (
    ExerciseDefinition(
        id="MKT-003", version="1.0", domain="Marketing Intelligence & Brand Strategy",
        name="Market Share", description="Measure brand share of the defined market using observed sales value.",
        type=ExerciseType.DESCRIPTIVE, business_question="What is the brand's share of the defined market?",
        required_inputs=("Brand Name", "Sales Value"), dimensions=("Brand Name",), measures=("Sales Value",),
        minimum_period=1, methodology="Aggregate observed sales value by brand and divide by total observed market sales value.",
        metrics=("market_share_pct",), engines=("market_intelligence.market_share_by_brand",),
        primary_visualizations=("VIZ-008", "VIZ-006"), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="MKT-004", version="1.0", domain="Marketing Intelligence & Brand Strategy",
        name="Market Summary", description="Summarize the observed market using the dimensions supported by the existing market summary capability.",
        type=ExerciseType.DESCRIPTIVE, business_question="What does the observed market look like across its supported dimensions?",
        required_inputs=("Therapeutic Class", "Sales Value", "Sales Units"),
        dimensions=("Therapeutic Class",), measures=("Sales Value", "Sales Units"), minimum_period=1,
        methodology="Use the existing market summary capability; no additional metrics are inferred here.",
        metrics=("market_summary",), engines=("market_intelligence.market_summary",),
        primary_visualizations=("VIZ-005",), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="MKT-010", version="1.0", domain="Marketing Intelligence & Brand Strategy",
        name="Manufacturer Share", description="Measure observed market share by manufacturer using sales value.",
        type=ExerciseType.DESCRIPTIVE, business_question="What share of the defined market is held by each manufacturer?",
        required_inputs=("Manufacturer", "Sales Value"), dimensions=("Manufacturer",), measures=("Sales Value",),
        minimum_period=1, methodology="Aggregate observed sales value by manufacturer and divide by total observed market sales value.",
        metrics=("manufacturer_market_share_pct",), engines=("market_intelligence.market_share_by_manufacturer",),
        primary_visualizations=("VIZ-008", "VIZ-006"), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="MKT-011", version="1.0", domain="Marketing Intelligence & Brand Strategy",
        name="White Space Opportunity", description="Identify opportunity signals using the existing recommendation capability only when its contract is validated.",
        type=ExerciseType.OPPORTUNITY, business_question="Where are potential commercial opportunity signals in the available data?",
        required_inputs=("Sales Value",), measures=("Sales Value",), minimum_period=1,
        methodology="No validated reusable White Space capability currently exists. The existing recommendation opportunity_analysis is a pass-through placeholder, so execution remains blocked rather than fabricating opportunity signals.",
        metrics=("opportunity_signal",), engines=("recommendation.opportunity_analysis",),
        primary_visualizations=("VIZ-014",), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="SAL-012", version="1.0", domain="Sales Intelligence & Performance",
        name="Sales Opportunity Analysis", description="Use the existing recommendation capability only after exact exercise semantics are validated.",
        type=ExerciseType.OPPORTUNITY, business_question="Where are actionable sales opportunity signals in the available data?",
        required_inputs=("Sales Value",), measures=("Sales Value",), minimum_period=1,
        methodology="No validated reusable Sales Opportunity capability currently exists. The existing recommendation opportunity_analysis is a pass-through placeholder, so execution remains blocked rather than fabricating opportunity signals.",
        metrics=("opportunity_signal",), engines=("recommendation.opportunity_analysis",),
        primary_visualizations=("VIZ-014",), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="HCP-015", version="1.0", domain="HCP/KOL", name="KOL Identification",
        description="Identify and score KOL candidates using observed scientific influence inputs.",
        type=ExerciseType.OPPORTUNITY, business_question="Which HCP/KOL candidates have the strongest observed influence signals?",
        required_inputs=("publication_count", "citation_count"), dimensions=("hcp",), measures=("publication_count", "citation_count"),
        minimum_period=1, methodology="Use the existing KOL scoring capability once its input/output contract is available and validated.",
        metrics=("kol_score",), engines=("medical_affairs.score_kols",), primary_visualizations=("VIZ-012", "VIZ-006"), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="TRD-019", version="1.0", domain="Trade/Distribution", name="Channel Performance",
        description="Compare observed channel performance using sales value and units.",
        type=ExerciseType.DIAGNOSTIC, business_question="How is performance distributed across channels?",
        required_inputs=("Distribution Channel", "Sales Value", "Sales Units"), dimensions=("Distribution Channel",),
        measures=("Sales Value", "Sales Units"), minimum_period=1, methodology="Use the existing channel performance capability after contract validation.",
        metrics=("channel_sales_value", "channel_sales_units"), engines=("gtm.channel_performance",),
        primary_visualizations=("VIZ-005", "VIZ-006"), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="FIN-008", version="1.0", domain="Pricing/Finance", name="Price Volume Analysis",
        description="Decompose observed commercial movement into price and volume signals using the existing finance capability.",
        type=ExerciseType.DIAGNOSTIC, business_question="How much of observed commercial movement is associated with price versus volume?",
        required_inputs=("Year", "Month", "Selling Price", "Sales Units"), measures=("Selling Price", "Sales Units"), minimum_period=2, methodology="Compare the earliest and latest observed periods, derive unit-weighted price and total volume for each period, then call the existing deterministic price-volume decomposition capability.",
        metrics=("price_effect", "volume_effect"), engines=("commercial_finance.price_volume_analysis",),
        primary_visualizations=("VIZ-009",), data_classification="INTERNAL",
    ),
    ExerciseDefinition(
        id="EXE-018", version="1.0", domain="Executive", name="Executive Decision Brief",
        description="Synthesize validated child evidence into an executive decision brief without introducing a new analytics engine.",
        type=ExerciseType.COMPOSITE, business_question="What decision-relevant findings, risks and options emerge from the validated evidence?",
        required_inputs=tuple(), minimum_period=1, methodology="Evidence synthesis over validated child Exercise Runs; no independent metric calculation.",
        metrics=(), engines=(), primary_visualizations=("VIZ-002", "VIZ-023", "VIZ-024"), data_classification="INTERNAL",
    ),
)
