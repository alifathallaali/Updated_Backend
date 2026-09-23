from app.visualization.chart_priority import prioritize_charts,chart_priority_score
def c(id,title,typ="bar"):
 return {"chartId":id,"chartType":typ,"meta":{"title":title},"data":[]}
def test_forecast_prefers_forecast_output_over_generic_trend():
 out=prioritize_charts([c("market-trend","Market trend","line"),c("forecast-output","Forecast output")],"forecast",["actual_vs_forecast","trend"])
 assert out[0]["chartId"]=="forecast-output"
 assert out[0]["presentationPriority"]["role"]=="primary"
def test_scenario_prefers_scenario_comparison():
 out=prioritize_charts([c("market-trend","Trend"),c("scenario-value","Scenario value comparison")],"scenario")
 assert out[0]["chartId"]=="scenario-value"
def test_launch_prefers_risk_score():
 out=prioritize_charts([c("market-trend","Trend"),c("launch-success","Launch success risk score")],"launch")
 assert out[0]["chartId"]=="launch-success"
def test_original_order_breaks_ties_stably():
 out=prioritize_charts([c("a","Other"),c("b","Other")],"generic")
 assert [x["chartId"] for x in out]==["a","b"]
def test_prioritization_does_not_mutate_input():
 charts=[c("x","Forecast output")]
 prioritize_charts(charts,"forecast")
 assert "presentationPriority" not in charts[0]
