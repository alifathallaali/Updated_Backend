from app.visualization import build_visualizations

ROWS=[
 {"period":"2026-01","brand_name":"A","manufacturer":"X","product":"A","sales_value":100,"sales_units":10},
 {"period":"2026-02","brand_name":"B","manufacturer":"Y","product":"B","sales_value":150,"sales_units":15},
]
def test_all_current_product_visualization_packs_are_safe():
    base={"metrics":{}}
    for i in range(1,15):
        charts=build_visualizations(f"product-{i:02d}",ROWS,base)
        assert isinstance(charts,list)
        for chart in charts:
            assert chart["chartId"]
            assert chart["chartType"]
            assert isinstance(chart["data"],list)
