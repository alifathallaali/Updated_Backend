"""Canonical visualization contract for PharmaLens AI."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ChartSpec:
    chart_id: str
    chart_type: str
    title: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    x_key: Optional[str] = None
    series: List[Dict[str, Any]] = field(default_factory=list)
    description: Optional[str] = None
    subtitle: Optional[str] = None
    insight: Optional[str] = None
    source: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_id": self.chart_id, "chart_type": self.chart_type,
            "title": self.title, "subtitle": self.subtitle,
            "description": self.description, "x_key": self.x_key,
            "series": self.series, "data": self.data,
            "insight": self.insight, "source": self.source,
            "filters": self.filters, "metadata": self.metadata,
        }
