import uuid
from datetime import datetime, timezone
from statistics import median as _median
from typing import Any


def number_of(row: dict, *keys: str) -> float:
    for key in keys:
        value = row.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str) and value.strip():
            try:
                return float(value)
            except ValueError:
                continue
    return 0.0


def text_of(row: dict, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
    return "Unknown"


def build_output(product_id: str, summary: str, metrics: dict, evidence: list[dict], warnings: list[str] | None = None) -> dict:
    warnings = warnings or []
    has_evidence = len(evidence) > 0
    return {
        "productId": product_id,
        "runId": str(uuid.uuid4()),
        "status": "partial" if warnings else "success",
        "summary": summary,
        "metrics": metrics,
        "evidence": evidence,
        "warnings": warnings,
        "confidence": {
            "score": 0.6 if warnings else (0.85 if has_evidence else 0.35),
            "level": "medium" if warnings else ("high" if has_evidence else "low"),
            "rationale": (
                "Output includes warnings about missing or incomplete canonical fields."
                if warnings
                else ("Output is supported by canonical evidence references." if has_evidence else "Output has limited supporting evidence.")
            ),
        },
        "generatedAt": int(datetime.now(timezone.utc).timestamp() * 1000),
    }


def grouped(rows: list[dict], keys: list[str]) -> list[dict]:
    groups: dict[str, dict] = {}
    for row in rows:
        label = text_of(row, *keys)
        current = groups.setdefault(label, {"label": label, "salesValue": 0.0, "salesUnits": 0.0})
        current["salesValue"] += number_of(row, "sales_value", "lc_value", "salesValue", "value")
        current["salesUnits"] += number_of(row, "sales_units", "units", "salesUnits")
    return sorted(groups.values(), key=lambda g: g["salesValue"], reverse=True)


def evidence_for(field_label: str, group: dict, source: str) -> list[dict]:
    return [
        {"field": field_label, "value": group["label"], "source": source},
        {"field": "sales_value", "value": group["salesValue"], "source": source},
        {"field": "sales_units", "value": group["salesUnits"], "source": source},
    ]


def median(values: list[float]) -> float:
    return float(_median(values)) if values else 0.0
