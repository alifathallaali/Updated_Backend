"""
Standard Product Engine Contracts & Response Builders.
Strictly enforces output formats for downstream Consumption (Copilot/UI/Reports).
"""

from typing import Any, Dict, List, Optional


def build_adapter_output(
    status: str,  # "success" | "partial" | "error" | "incomplete"
    summary: str,
    metrics: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    warnings: List[str],
    data_readiness: Dict[str, Any],
    provenance: Optional[Dict[str, Any]] = None,
    extra_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build unified standard engine response format."""
    payload = {
        "status": status,
        "summary": summary,
        "metrics": metrics,
        "evidence": evidence,
        "warnings": warnings,
        "confidence": {
            "score": 1.0 if status == "success" else 0.5,
            "level": "HIGH" if status == "success" else "LOW",
        },
        "data_readiness": data_readiness,
        "provenance": provenance or {},
    }

    if extra_payload:
        payload.update(extra_payload)

    return payload


def build_incomplete_output(
    module_name: str,
    data_readiness: Dict[str, Any],
    provenance: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Standard response for missing datasets without guessing or hallucinations."""
    missing_str = ", ".join(data_readiness.get("missing_fields", []))
    summary = f"Insufficient data available to support {module_name} conclusions. Missing required canonical fields: [{missing_str}]."

    return build_adapter_output(
        status="incomplete",
        summary=summary,
        metrics={},
        evidence=[],
        warnings=[f"Execution skipped due to missing required canonical schema keys: {missing_str}"],
        data_readiness=data_readiness,
        provenance=provenance,
    )
