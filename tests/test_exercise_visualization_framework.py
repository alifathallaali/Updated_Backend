from app.visualization import build_exercise_visualizations, resolve_profile

ROWS=[
 {"period":"2026-01","brand_name":"A","manufacturer":"X","sales_value":100,"sales_units":10},
 {"period":"2026-02","brand_name":"B","manufacturer":"Y","sales_value":150,"sales_units":15},
]

def test_future_exercise_resolves_by_family_without_custom_renderer():
    family, profile = resolve_profile("exercise-heor-cost-effectiveness", name="HEOR value assessment")
    assert family == "market_access"
    charts = build_exercise_visualizations("exercise-heor-cost-effectiveness", ROWS, {"metrics":{"icer":1200,"qaly":2.1}}, name="HEOR value assessment")
    assert charts
    assert all("chartId" in chart for chart in charts)

def test_unknown_exercise_has_safe_generic_visuals():
    family, _ = resolve_profile("exercise-250-custom")
    assert family == "generic"
    charts = build_exercise_visualizations("exercise-250-custom", ROWS, {"metrics":{"score":88}})
    assert charts
