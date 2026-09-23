from app.engines.intent_resolver import resolve_dataset_goal


def test_goal_resolver_preserves_governed_routing_contract():
    result = resolve_dataset_goal(["period", "sales_value", "sales_units", "product"], "forecast product sales")
    assert result["intent"] == "predict"
    assert result["trust"]["rawRowsSentToLLM"] is False
    assert result["trust"]["routingStatus"] == "calculated"
    assert isinstance(result["alternatives"], list)

def test_persona_is_soft_priority_not_compatibility_override():
    r=resolve_dataset_goal(["period_month","sales_value","brand_name"],"understand performance",persona="brand_manager")
    assert r["persona"]=="brand_manager"
    assert r["recommendedExercise"] is not None
    assert r["trust"]["rawRowsSentToLLM"] is False
