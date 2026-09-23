from app.visualization import build_visualizations

def test_market_visualizations():
    rows = [
        {"period":"2026-01","brand_name":"A","manufacturer":"X","sales_value":100},
        {"period":"2026-02","brand_name":"A","manufacturer":"X","sales_value":120},
        {"period":"2026-02","brand_name":"B","manufacturer":"Y","sales_value":80},
    ]
    charts = build_visualizations("product-01", rows, {"metrics":{}})
    assert charts
    assert charts[0]["chartType"] == "line"
    assert all("chartId" in c for c in charts)
