"""
Common Data Extraction and Readiness Helpers.
Guarantees deterministic handling of raw canonical dataset rows.
"""

from typing import Any, Dict, List, Tuple


def get_value(row: Dict[str, Any], *keys: str) -> float:
    """Extract float value safely from a row using flexible fallback keys."""
    for key in keys:
        raw = row.get(key)
        if raw is None:
            continue
        try:
            val = float(raw)
            if val == val:  # Check for NaN
                return val
        except (TypeError, ValueError):
            pass
    return 0.0


def get_label(row: Dict[str, Any], *keys: str, default: str = "Unknown") -> str:
    """Extract clean string value safely from a row using flexible fallback keys."""
    for key in keys:
        raw = row.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return default


def check_readiness(rows: List[Dict[str, Any]], required_fields: List[str]) -> Dict[str, Any]:
    """Check dataset readiness against required logical keys."""
    if not rows:
        return {
            "status": "INCOMPLETE",
            "required_fields": required_fields,
            "available_fields": [],
            "missing_fields": required_fields,
            "total_rows": 0,
        }

    available: set = set()
    for row in rows:
        available.update(k for k, v in row.items() if v not in (None, "", "null"))

    missing = [field for field in required_fields if field not in available]

    return {
        "status": "READY" if not missing else "INCOMPLETE",
        "required_fields": required_fields,
        "available_fields": sorted(list(available)),
        "missing_fields": missing,
        "total_rows": len(rows),
    }


def aggregate_by_fields(
    rows: List[Dict[str, Any]],
    group_keys: Tuple[str, ...],
    value_keys: Tuple[str, ...],
) -> List[Dict[str, Any]]:
    """Group and aggregate numeric values from canonical rows deterministically."""
    grouped: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        # Construct group key label
        g_label = " - ".join([get_label(row, k) for k in group_keys])
        
        if g_label not in grouped:
            grouped[g_label] = {
                "group_key": g_label,
                "row_count": 0,
                **{vk: 0.0 for vk in value_keys},
            }

        grouped[g_label]["row_count"] += 1
        for vk in value_keys:
            grouped[g_label][vk] += get_value(row, vk)

    return list(grouped.values())


def build_evidence(
    field: str,
    value: Any,
    calculation: str,
    source: str = "DatasetVersion",
    label: str = "Calculated",
) -> Dict[str, Any]:
    """Construct a transparent lineage/evidence object for output metrics."""
    return {
        "field": field,
        "value": value,
        "source": source,
        "calculation": calculation,
        "label": label,
    }
