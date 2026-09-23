from .tender_parser import parse_tender
from .tender_eligibility import assess_eligibility
from .tender_competition import assess_competition
from .tender_finance import tender_financials
from .tender_risk import assess_tender_risk
from .tender_scoring import mcda_score
from .tender_decision import tender_decision

def analyze_tender(parameters):
    tender = parse_tender(parameters.get("tender", parameters))

    eligibility = assess_eligibility(
        tender.eligibility_requirements,
        parameters.get("company_facts", {}),
    )

    competition = assess_competition(
        parameters.get("matched_products", []),
        parameters.get("competitor_facts", []),
    )

    quantity = float(parameters.get("quantity", 0.0))
    bid_price = float(parameters.get("bid_price", 0.0))
    unit_cost = float(parameters.get("unit_cost", 0.0))

    financials = tender_financials(
        quantity,
        bid_price,
        unit_cost,
        float(parameters.get("fixed_costs", 0.0)),
    )

    risk = assess_tender_risk(
        eligibility,
        financials,
        parameters.get("supply_capacity"),
        quantity,
    )

    criteria = parameters.get("criteria_scores", {
        "eligibility": 1.0 if eligibility["eligible"] else 0.0,
        "financial": max(0.0, min(1.0, financials["margin"])),
        "competition": max(0.0, min(1.0, 1.0 - competition["competitor_count"] / 10.0)),
        "risk": max(0.0, min(1.0, 1.0 - min(risk["risk_count"] / 5.0, 1.0))),
    })

    weights = parameters.get("weights", {
        "eligibility": 0.25,
        "financial": 0.35,
        "competition": 0.20,
        "risk": 0.20,
    })

    mcda = mcda_score(criteria, weights)
    decision = tender_decision(eligibility, risk, mcda)

    return {
        "tender": tender,
        "eligibility": eligibility,
        "competition": competition,
        "financials": financials,
        "risk": risk,
        "mcda": mcda,
        "decision": decision,
    }
