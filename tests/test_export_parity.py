from app.reports.export_parity import prepare_export_output

def chart(cid,rank,data):
 return {"chartId":cid,"chartType":"bar","meta":{"title":cid},"xKey":"x","series":[{"dataKey":"v"}],"data":data,"presentationPriority":{"rank":rank,"role":"primary" if rank==1 else "diagnostic"}}

def test_export_keeps_ui_priority_order():
 out=prepare_export_output({"visualizations":[chart("b",2,[{"x":"B","v":2}]),chart("a",1,[{"x":"A","v":1}])]})
 assert [x["chartId"] for x in out["visualizations"]]==["a","b"]
 assert out["exportPresentation"]["primaryChartId"]=="a"

def test_export_suppresses_empty_visuals():
 out=prepare_export_output({"visualizations":[chart("empty",1,[]),chart("good",2,[{"x":"A","v":1}])]})
 assert [x["chartId"] for x in out["visualizations"]]==["good"]

def test_export_applies_same_top_n_adaptation():
 data=[{"x":str(i),"v":i} for i in range(30)]
 out=prepare_export_output({"visualizations":[chart("rank",1,data)]})
 assert len(out["visualizations"][0]["data"])==15
 assert out["visualizations"][0]["presentationAdaptation"]["topNApplied"] is True
