from app.visualization.executive_narrative import build_executive_narrative
def test_narrative_uses_existing_summary():
 r=build_executive_narrative({"summary":"Sales increased.","metrics":{"growth":12},"evidence":[],"warnings":[],"confidence":{}},[])
 assert r["whatHappened"]=="Sales increased."
 assert r["grounding"]["causalInferenceAdded"] is False
def test_metric_fallback_when_summary_missing():
 r=build_executive_narrative({"metrics":{"sales_value":100,"growth":5},"evidence":[],"warnings":[]},[])
 assert "Sales Value: 100" in r["whatHappened"]
def test_watchouts_come_from_warnings():
 r=build_executive_narrative({"summary":"x","metrics":{},"evidence":[],"warnings":["Limited history"],"confidence":{}},[])
 assert r["watchouts"]==["Limited history"]
def test_next_analysis_is_navigation_not_claim():
 r=build_executive_narrative({"summary":"x"},[{"exerciseId":"product-02","name":"Growth"}])
 assert r["nextAnalysis"][0]["exerciseId"]=="product-02"
 assert "Related next analysis" in r["nextAnalysis"][0]["reason"]
