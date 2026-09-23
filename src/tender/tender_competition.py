def assess_competition(matched_products, competitor_facts):
    return {
        "matched_products": matched_products,
        "competitor_facts": competitor_facts,
        "competitor_count": len(competitor_facts),
    }
