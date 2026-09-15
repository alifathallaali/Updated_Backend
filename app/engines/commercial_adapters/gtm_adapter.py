"""
Slice 3: Go-To-Market (GTM) Basic Adapter (Product-16)
Provides channel and product breakdown metrics without making speculative assumptions.
"""

from typing import Any, Dict, List
from ._common import check_readiness, aggregate_by_fields, build_evidence
from .contracts import build_adapter_output, build_incomplete_output


def run_gtm_adapter(rows: List[Dict[str, Any]], input_: Dict[str, Any]) -> Dict[str, Any]:
    required_fields = ["product", "period", "sales_value"]
    readiness = check_readiness(rows, required_fields)

    if readiness["status"] != "READY":
        return build_incomplete_output("Go-To-Market (GTM) Analysis", readiness)

    # Channel Aggregation
    by_channel = aggregate_by_fields(
        rows,
        group_keys=("distribution_channel", "channel"),
        value_keys=("sales_value", "sales_units"),
    )

    # Product Breakdown
    by_product = aggregate_by_fields(
        rows,
        group_keys=("product", "brand"),
        value_keys=("sales_value", "sales_units"),
    )

    total_sales = sum(c["sales_value"] for c in by_channel)
    total_units = sum(c["sales_units"] for c in by_channel)

    evidence = [
        build_evidence(
            field="gtm.channel_aggregation",
            value=len(by_channel),
            calculation="group_by(distribution_channel)",
        ),
        build_evidence(
            field="gtm.total_sales",
            value=total_sales,
            calculation="sum(sales_value)",
        ),
    ]

    return build_adapter_output(
        status="success",
        summary="Go-To-Market performance aggregated across distribution channels and products.",
        metrics={
            "channel_count": len(by_channel),
            "product_count": len(by_product),
            "total_sales_value": total_sales,
            "total_sales_units": total_units,
        },
        evidence=evidence,
        warnings=[],
        data_readiness=readiness,
        extra_payload={
            "by_channel": by_channel,
            "by_product": by_product,
        },
    )
