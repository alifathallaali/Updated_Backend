"""
Slice 2: Recommendation Adapter (Product-15)
Processes canonical dataset rows and generates evidence-backed strategic recommendations.
"""

from typing import Any, Dict, List
from ._common import check_readiness, get_value, get_label, build_evidence
from .contracts import build_adapter_output, build_incomplete_output


def run_recommendation_adapter(rows: List[Dict[str, Any]], input_: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = ["product", "sales_value", "period"]
    readiness = check_readiness(rows, required_fields)

    if readiness["status"] != "READY":
        return build_incomplete_output("Recommendation Engine", readiness)

    # Group by product
    products_map: Dict[str, Dict[str, Any]] = {}
    total_sales = 0.0

    for row in rows:
        product = get_label(row, "product", "brand", "sku")
        sales = get_value(row, "sales_value", "revenue", "sales")
        growth = get_value(row, "growth", "growth_pct", "growth_rate")

        total_sales += sales

        if product not in products_map:
            products_map[product] = {
                "product": product,
                "sales_value": 0.0,
                "growth_observations": [],
            }

        products_map[product]["sales_value"] += sales
        products_map[product]["growth_observations"].append(growth)

    recommendations: List[Dict[str, Any]] = []
    evidence_chain: List[Dict[str, Any]] = []

    for prod_name, p_data in products_map.items():
        avg_growth = (
            sum(p_data["growth_observations"]) / len(p_data["growth_observations"])
            if p_data["growth_observations"]
            else 0.0
        )

        # Risk Rule: Negative Growth despite active sales
        if avg_growth < 0 and p_data["sales_value"] > 0:
            rec = {
                "type": "risk",
                "priority": "high",
                "product": prod_name,
                "title": f"Declining Revenue Trend for {prod_name}",
                "reason": "Observed negative commercial growth across dataset periods.",
                "evidence": {
                    "sales_value": p_data["sales_value"],
                    "average_growth_pct": round(avg_growth, 2),
                },
            }
            recommendations.append(rec)

            evidence_chain.append(
                build_evidence(
                    field=f"recommendation.{prod_name}.negative_growth",
                    value=round(avg_growth, 2),
                    calculation=f"avg(growth) across {len(p_data['growth_observations'])} records",
                )
            )

    evidence_chain.append(
        build_evidence(
            field="total_sales_value",
            value=total_sales,
            calculation="sum(sales_value)",
        )
    )

    return build_adapter_output(
        status="success",
        summary=f"Generated {len(recommendations)} evidence-backed recommendations from {len(products_map)} products.",
        metrics={
            "products_analyzed": len(products_map),
            "recommendations_count": len(recommendations),
            "total_sales_value": total_sales,
        },
        evidence=evidence_chain,
        warnings=[],
        data_readiness=readiness,
        extra_payload={"recommendations": recommendations},
    )
