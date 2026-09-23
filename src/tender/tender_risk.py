def assess_tender_risk(eligibility, financials, supply_capacity=None, tender_quantity=None):
    risks = []
    if not eligibility.get("eligible", False):
        risks.append("Eligibility requirements are not fully satisfied.")
    if financials.get("margin", 0.0) < 0:
        risks.append("Projected margin is negative.")
    if (
        supply_capacity is not None
        and tender_quantity is not None
        and supply_capacity < tender_quantity
    ):
        risks.append("Available supply capacity is below tender quantity.")
    return {
        "risk_count": len(risks),
        "risks": risks,
        "risk_level": "high" if len(risks) >= 2 else "moderate" if risks else "low",
    }
