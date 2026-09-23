from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

class EvidenceType(str, Enum):
    FACT = "FACT"
    CALCULATION = "CALCULATION"
    FORECAST = "FORECAST"
    INTERPRETATION = "INTERPRETATION"
    RECOMMENDATION = "RECOMMENDATION"
    WARNING = "WARNING"

@dataclass
class EvidenceItem:
    evidence_type: EvidenceType
    statement: str
    source: Optional[str] = None
    field: Optional[str] = None
    value: Any = None

@dataclass
class ResultMetadata:
    engine: str
    engine_version: str = "v1"
    data_source: Optional[str] = None
    data_period: Optional[str] = None
    data_version: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: Optional[float] = None

@dataclass
class EngineResult:
    status: str
    tool: str
    data: Any = None
    metadata: Optional[ResultMetadata] = None
    evidence: List[EvidenceItem] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def success(cls, tool, data, metadata=None, evidence=None, warnings=None):
        return cls(
            status="success", tool=tool, data=data, metadata=metadata,
            evidence=evidence or [], warnings=warnings or []
        )

    @classmethod
    def failure(cls, tool, error, warnings=None):
        return cls(status="error", tool=tool, error=error, warnings=warnings or [])
