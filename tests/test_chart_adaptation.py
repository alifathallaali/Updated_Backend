from app.visualization.chart_adaptation import adapt_chart
def c(n,typ="bar",long=False):
 return {"chartId":"x","chartType":typ,"meta":{"title":"X"},"xKey":"name","series":[{"dataKey":"value"}],
 "data":[{"name":(("Very long pharmaceutical category label "+str(i)) if long else str(i)),"value":i} for i in range(n)]}
def test_long_ranking_is_top_15():
 out=adapt_chart(c(30))
 assert len(out["data"])==15 and out["presentationAdaptation"]["topNApplied"]
def test_long_labels_use_horizontal_bar():
 out=adapt_chart(c(8,long=True))
 assert out["presentationAdaptation"]["orientation"]=="horizontal"
def test_dense_chart_requests_mobile_scroll():
 out=adapt_chart(c(12,"line"))
 assert out["presentationAdaptation"]["mobile"]=="horizontal_scroll"
def test_small_chart_is_compact_mobile():
 out=adapt_chart(c(4,"line"))
 assert out["presentationAdaptation"]["mobile"]=="compact"
def test_original_chart_not_mutated():
 original=c(30); adapt_chart(original)
 assert len(original["data"])==30 and "presentationAdaptation" not in original
