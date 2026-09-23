def tender_decision(eligibility, risk, mcda):
    reasons = []
    if not eligibility.get("eligible", False):
        reasons.append("Eligibility is incomplete.")
    if risk.get("risk_level") == "high":
        reasons.append("Tender risk is high.")
    return {
        "decision_support_status": (
            "requires_review" if reasons else "ready_for_business_review"
        ),
        "mcda_score": float(mcda.get("score", 0.0)),
        "reasons": reasons,
        "note": (
            "Decision support only. Final bid approval remains subject to "
            "authorized commercial, financial, supply, legal and procurement review."
        ),
    }
