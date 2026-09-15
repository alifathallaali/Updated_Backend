"""
Slice 4: Commercial Finance Adapter (Product-17)
Handles strictly verified financial performance metrics (ROI, Budget Variance) safely.
"""

from typing import Any, Dict, List
from ._common import check_readiness, get_value, build_evidence
from .contracts import build_adapter_output, build_incomplete_output


def run_commercial_finance_adapter(rows: List[Dict[str, Any]], input_: Dict[str, Any]) -> Dict[str, Any]:
    required_base = ["period", "sales_value"]
    readiness = check_readiness(rows, required_base)

    if readiness["status"] != "READY":
        return build_incomplete_output("Commercial Finance Engine", readiness)

    total_sales = sum(get_value(r, "sales_value", "actual_value", "revenue") for r in rows)
    total_budget = sum(get_value(r, "budget", "planned_value") for r in rows)
    total_investment = sum(get_value(r, "investment", "cost") for r in rows)

    metrics: Dict[str, Any] = {
        "total_revenue": total_sales,
    }

    evidence: List[Dict[str, Any]] = [
        build_evidence("financial.revenue", total_sales, "sum(sales_value)")
    ]
    warnings: List[str] = []

    # Safe Budget Variance Calculation
    if "budget" in readiness["available_fields"] or "planned_value" in readiness["available_fields"]:
        budget_variance = total_sales - total_budget
        achievement_pct = (total_sales / total_budget * 100) if total_budget > 0 else 0.0

        metrics["total_budget"] = total_budget
        metrics["budget_variance"] = budget_variance
        metrics["budget_achievement_pct"] = round(achievement_pct, 2)

        evidence.append(build_evidence("financial.budget_variance", budget_variance, "total_sales - total_budget"))
    else:
        warnings.append("Budget variance omitted: 'budget' field is missing from dataset.")

    # Safe ROI Calculation
    if "investment" in readiness["available_fields"] or "cost" in readiness["available_fields"]:
        if total_investment > 0:
            roi = ((total_sales - total_investment) / total_investment) * 100
            metrics["investment"] = total_investment
            metrics["roi_pct"] = round(roi, 2)
            evidence.append(build_evidence("financial.roi", roi, "((revenue - investment) / investment) * 100"))
        else:
            warnings.append("ROI calculation skipped: Total recorded investment is 0.")
    else:
        warnings.append("ROI calculation omitted: 'investment' field is missing from dataset.")

    return build_adapter_output(
        status="success" if metrics else "incomplete",
        summary="Commercial finance summary calculated from canonical dataset.",
        metrics=metrics,
        evidence=evidence,
        warnings=warnings,
        data_readiness=readiness,
    )
