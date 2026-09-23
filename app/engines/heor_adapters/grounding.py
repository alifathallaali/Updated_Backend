"""Copilot grounding guardrails for HEOR routing."""
def heor_grounding_requirement(rec: dict | None, filters: dict | None) -> dict | None:
    if rec and rec.get("exerciseId") == "product-18" and not ((filters or {}).get("heor")):
        return {
            "status":"PARTIAL","requiresStructuredInputs":True,
            "requiredInputs":["product.cost","product.effect","comparator.cost","comparator.effect"],
            "reason":"HEOR was identified, but clinical/economic assumptions are not inferred from commercial rows. Supply them through the existing Product Run filters.heor payload.",
        }
    return None
