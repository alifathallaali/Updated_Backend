from app.visualization.chart_quality import assess_chart_quality,apply_chart_quality
def c(data,typ="bar",series=None):
 return {"chartId":"x","chartType":typ,"meta":{"title":"X"},"data":data,"xKey":"x","series":series or [{"dataKey":"value"}]}
def test_empty_chart_is_suppressed():
 rendered,suppressed=apply_chart_quality([c([])])
 assert rendered==[] and suppressed[0]["issues"]==["no_data"]
def test_single_point_line_is_not_presented_as_trend():
 q=assess_chart_quality(c([{"x":"Jan","value":10}],"line"))
 assert not q["usable"] and "single_point_trend" in q["issues"]
def test_valid_line_is_usable():
 q=assess_chart_quality(c([{"x":"Jan","value":10},{"x":"Feb","value":12}],"line"))
 assert q["usable"]
def test_dense_bar_gets_warning_not_silently_deleted():
 q=assess_chart_quality(c([{"x":str(i),"value":i} for i in range(40)]))
 assert q["usable"] and "too_many_categories" in q["warnings"]
def test_non_numeric_series_is_unusable():
 q=assess_chart_quality(c([{"x":"A","value":"unknown"}]))
 assert not q["usable"] and "no_numeric_series" in q["issues"]
