def tender_financials(quantity, bid_price, unit_cost, fixed_costs=0.0):
    revenue = quantity * bid_price
    variable_cost = quantity * unit_cost
    contribution = revenue - variable_cost
    profit = contribution - fixed_costs
    return {
        "revenue": revenue,
        "variable_cost": variable_cost,
        "contribution": contribution,
        "fixed_costs": fixed_costs,
        "profit": profit,
        "margin": profit / revenue if revenue else 0.0,
    }
