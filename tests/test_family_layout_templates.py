from app.visualization.layout_templates import FAMILY_LAYOUTS,get_family_layout
from app.visualization.exercise_catalog import get_exercise_presentation

def test_major_families_have_layouts():
    for family in ("market","forecast","scenario","sales","finance","supply","inventory","market_access"):
        assert family in FAMILY_LAYOUTS
        assert FAMILY_LAYOUTS[family]["template"]

def test_forecast_and_finance_are_not_generic_compositions():
    assert get_family_layout("forecast")["template"] == "forecast_cockpit"
    assert get_family_layout("finance")["template"] == "finance_variance"

def test_presentation_contract_contains_layout():
    p=get_exercise_presentation("product-06")
    assert p["layout"]["family"]=="forecast"
    assert p["layout"]["primary_height"]=="xl"

def test_unknown_family_falls_back_safely():
    assert get_family_layout("future_family")["template"]=="executive_analysis"
