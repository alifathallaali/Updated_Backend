from app.engines.engine_registry import ENGINE_REGISTRY, run_product_engine
from app.engines.product_catalog import get_product_by_id
from app.engines.intent_resolver import resolve_dataset_goal
from src.engines.target_planning.target_engine import top_down,bottom_up,iterative_reconcile
import pandas as pd

ROWS=[
 {"territory":"North","sales_rep":"Rep A","hcp":"Dr A","hco":"H1","potential":100,"target":1000,"actual":800,"calls":2,"planned_calls":3,"required_frequency":2,"capacity":5,"period":"2026-01","product":"Brand X","sales_units":10,"sales_value":800},
 {"territory":"North","sales_rep":"Rep A","hcp":"Dr B","hco":"H1","potential":80,"target":1000,"actual":600,"calls":0,"planned_calls":2,"required_frequency":1,"capacity":5,"period":"2026-02","product":"Brand X","sales_units":12,"sales_value":600},
 {"territory":"South","sales_rep":"Rep B","hcp":"Dr C","hco":"H2","potential":40,"target":500,"actual":550,"calls":2,"planned_calls":2,"required_frequency":2,"capacity":4,"period":"2026-02","product":"Brand Y","sales_units":8,"sales_value":550},
]

def test_registry_catalog_and_standard_contract():
    assert "product-13" in ENGINE_REGISTRY
    assert "Field Force Planner" in get_product_by_id("product-13")["name"]
    out=run_product_engine("product-13",ROWS,{"filters":{}})
    for key in ("metrics","evidence","warnings","confidence","trust","visualizations"): assert key in out
    assert out["metrics"]["territories"]==2 and out["metrics"]["sales_reps"]==2

def test_sfe_math_target_reach_frequency_plan_capacity():
    out=run_product_engine("product-13",ROWS,{"filters":{}})
    m=out["metrics"]
    assert round(m["achievement_pct"],2)==78.0
    assert round(m["reach_pct"],2)==66.67
    assert round(m["average_frequency"],2)==2.0
    assert round(m["frequency_compliance_pct"],2)==66.67
    assert round(m["plan_adherence_pct"],2)==57.14
    assert round(m["capacity_utilization_pct"],2)==50.0

def test_priority_and_manager_outputs():
    ff=run_product_engine("product-13",ROWS,{"filters":{}})["field_force"]
    assert ff["priorities"][0]["customer"] in {"Dr A","Dr B"}
    assert ff["manager_review"]["off_track"] is True
    assert ff["planning"]["daily_priority_queue"]

def test_missing_input_guardrails():
    out=run_product_engine("product-13",[{"territory":"N","sales_rep":"R"}],{"filters":{}})
    assert any("Target-vs-actual" in w for w in out["warnings"])
    assert out["field_force"]["priorities"]==[]
    incomplete=run_product_engine("product-13",[{"territory":"N"}],{"filters":{}})
    assert any("representative" in w.lower() or "sales_rep" in w.lower() for w in incomplete["warnings"])

def test_intent_routes_field_force():
    route=resolve_dataset_goal(list(ROWS[0]),"Which HCPs should my med rep prioritize and where are coverage and frequency gaps?",persona="field_force")
    assert route["recommendedExercise"]["exerciseId"]=="product-13"

def test_existing_forecast_recommendation_scenario_finance_reuse():
    out=run_product_engine("product-13",ROWS,{"filters":{"field_force":{"include_scenario":True,"include_finance":True}}})
    reused=out["provenance"]["reused_engines"]
    assert "app.engines.strategy_engines.run_forecasting" in reused
    assert "app.engines.commercial_adapters.run_recommendation_adapter" in reused
    assert "app.engines.strategy_engines.run_scenario_planning" in reused
    assert "app.engines.commercial_adapters.run_commercial_finance_adapter" in reused

def test_smart_target_top_down_bottom_up_iterative_reuse():
    ct={"target_units":100.0,"target_value":1000.0}
    opp=pd.DataFrame([{"Region":"A","Opportunity_Score":0.8},{"Region":"B","Opportunity_Score":0.2}])
    td=top_down(ct,opp); bu=bottom_up(td); rec=iterative_reconcile(ct,td)
    assert round(bu["target_units"],6)==100 and round(bu["target_value"],6)==1000
    assert round(rec["Target_Units"].sum(),6)==100 and round(rec["Target_Value"].sum(),6)==1000

def test_smart_target_planning_adapter_delegates_when_explicitly_requested():
    rows=[dict(r, period="2025-01") for r in ROWS]
    out=run_product_engine("product-13",rows,{"filters":{"field_force":{"target_planning":{"base_year":2025,"target_year":2026,"growth_rate":0.1,"region_opportunity_rows":[{"Region":"North","MAT RX 2025":100,"RX Growth %":0.1},{"Region":"South","MAT RX 2025":50,"RX Growth %":0.05}]}}}})
    assert "src.engines.target_planning.target_engine" in out["provenance"]["reused_engines"]
    assert out["field_force"]["reused_outputs"]["smart_target_planning"]["top_down"]

def test_visualization_report_and_copilot_grounding_payload_shape():
    out=run_product_engine("product-13",ROWS,{"filters":{}})
    assert out["visualizations"]
    assert out["trust"]["rawRowsSentToLLM"] is False
    assert out["evidence"] and out["confidence"]["score"]>0
