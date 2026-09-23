from __future__ import annotations
from typing import Any
from .schemas import CanonicalResult

def normalize_sales_trend_result(*, rows: list[dict[str, Any]], start_value: float, end_value: float,
                                  growth_pct: float, quality: dict, lineage: dict) -> CanonicalResult:
    direction = "increased" if growth_pct > 0 else "declined" if growth_pct < 0 else "was flat"
    finding = {
        "id": "SAL-008-F001",
        "statement": f"Sales value {direction} by {abs(growth_pct):.1f}% from the first to the last available period.",
        "evidence_type": "CALCULATION",
        "value": growth_pct,
    }
    return CanonicalResult(
        executive_summary=f"Sales value {direction} by {abs(growth_pct):.1f}% over the available period.",
        key_findings=[finding],
        metrics=[
            {"id": "sales_start", "label": "First-period sales", "value": start_value, "evidence_type": "FACT"},
            {"id": "sales_end", "label": "Last-period sales", "value": end_value, "evidence_type": "FACT"},
            {"id": "sales_growth_pct", "label": "Sales growth", "value": growth_pct, "unit": "%", "evidence_type": "CALCULATION"},
        ],
        drivers=[], risks=[{"id": "SAL-008-R001", "statement": "Recent decline should be investigated for channel, brand, territory, price and volume drivers before action."}],
        opportunities=[{"id": "SAL-008-O001", "statement": "Use available dimensions to decompose the trend before assigning a commercial action."}],
        recommendations=[{"id": "SAL-008-RC001", "statement": "Investigate the latest-period decline by available commercial dimensions before setting a corrective action."}],
        assumptions=["Growth is calculated from the first and last available periods in the supplied dataset."],
        data_quality=quality,
        lineage=lineage,
        metadata={"rows": rows},
    )
