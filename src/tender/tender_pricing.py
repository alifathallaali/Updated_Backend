def calculate_bid_price(cost, target_margin, logistics_cost=0.0, other_costs=0.0):
    if target_margin < 0 or target_margin >= 1:
        raise ValueError("target_margin must be >= 0 and < 1")
    total_cost = cost + logistics_cost + other_costs
    return total_cost / (1.0 - target_margin)

def margin_from_price(bid_price, total_cost):
    if bid_price <= 0:
        return None
    return (bid_price - total_cost) / bid_price
