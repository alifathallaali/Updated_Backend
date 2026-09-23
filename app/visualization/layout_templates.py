"""Presentation composition by exercise family.

Layouts describe how existing governed result elements are composed. They do not
change analytics, KPIs, evidence, or chart calculations.
"""
FAMILY_LAYOUTS = {
    "market": {"template":"market_overview","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"trend_or_share"},
    "company": {"template":"competitive_profile","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"ranking_or_trend"},
    "molecule": {"template":"molecule_landscape","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"trend_or_ranking"},
    "product": {"template":"product_performance","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"trend"},
    "forecast": {"template":"forecast_cockpit","primary_height":"xl","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"actual_vs_forecast"},
    "scenario": {"template":"scenario_compare","primary_height":"xl","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"scenario_comparison"},
    "launch": {"template":"launch_readiness","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"risk_or_score"},
    "sales": {"template":"sales_execution","primary_height":"lg","diagnostic_columns":3,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"achievement_or_ranking"},
    "finance": {"template":"finance_variance","primary_height":"xl","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"variance_or_waterfall"},
    "supply": {"template":"supply_control","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"units_or_coverage"},
    "inventory": {"template":"inventory_risk","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"risk_or_cover"},
    "market_access": {"template":"access_decision","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"opportunity_or_access"},
    "medical": {"template":"medical_insights","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"trend"},
    "quality": {"template":"quality_risk","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"risk_or_trend"},
    "generic": {"template":"executive_analysis","primary_height":"lg","diagnostic_columns":2,"sections":["kpis","primary","diagnostics","evidence"],"primary_hint":"first_available"},
}

def get_family_layout(family: str) -> dict:
    return {"family": family, **FAMILY_LAYOUTS.get(family, FAMILY_LAYOUTS["generic"])}
