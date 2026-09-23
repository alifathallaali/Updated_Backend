from types import SimpleNamespace
from app.reports.pdf_report import build_decision_brief_pdf
from app.reports.pptx_report import build_decision_brief_pptx

OUTPUT={
 "summary":"Test","metrics":{"sales":100},
 "evidence":[{"field":"sales","value":100,"source":"canonical"}],
 "confidence":{"score":0.8,"level":"high","rationale":"test"},
 "visualizations":[
  {"chartId":"a","chartType":"bar","meta":{"title":"A"},"xKey":"category","series":[{"dataKey":"value"}],"data":[{"category":"X","value":10}]},
  {"chartId":"b","chartType":"line","meta":{"title":"B"},"xKey":"period","series":[{"dataKey":"value"}],"data":[{"period":"2026-01","value":20}]},
 ],
}
def selected_output(output, body):
 selected=set(body.selected_chart_ids or [])
 filtered=dict(output)
 if selected: filtered["visualizations"]=[c for c in output.get("visualizations",[]) if c.get("chartId") in selected]
 if not body.include_metrics: filtered["metrics"]={}
 if not body.include_evidence: filtered["evidence"]=[]
 return filtered

def test_selection_contract():
 body=SimpleNamespace(selected_chart_ids=["b"],include_metrics=True,include_evidence=False)
 out=selected_output(OUTPUT,body)
 assert [x["chartId"] for x in out["visualizations"]]==["b"]
 assert out["evidence"]==[]

def test_report_renderers_accept_visualizations():
 assert build_decision_brief_pdf("product-01","partial",OUTPUT)[:4]==b"%PDF"
 assert build_decision_brief_pptx("product-01","partial",OUTPUT)[:2]==b"PK"
