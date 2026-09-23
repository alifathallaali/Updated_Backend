from app.engines.engine_registry import ENGINE_REGISTRY, run_product_engine
from app.engines.product_catalog import get_product_by_id
from app.engines.intent_resolver import resolve_dataset_goal
from app.mapping_engine import suggest_mapping
from app.schemas import ProductRunFromDatasetVersionRequest
from src.engines.hospital_procurement.procurement import (
    safety_stock,reorder_point,net_procurement_requirement,buyer_tender_comparison,supplier_kpis
)

ROWS=[
 {"product":"IV Cannula 20G","consumption_quantity":3044,"inventory_on_hand":1000,"lead_time_days":14,"daily_demand_std":10,"open_po_quantity":200,"contract_covered_quantity":100,"expected_unit_cost":4,"budget":4000,"supplier":"Vendor A","ordered_quantity":1000,"received_quantity":950,"promised_lead_time_days":10,"actual_lead_time_days":9},
 {"product":"Syringe 10ml","consumption_quantity":1522,"inventory_on_hand":1200,"lead_time_days":7,"daily_demand_std":5,"open_po_quantity":0,"contract_covered_quantity":0,"expected_unit_cost":2,"budget":2000,"supplier":"Vendor A","ordered_quantity":500,"received_quantity":500,"promised_lead_time_days":8,"actual_lead_time_days":8},
]

def test_registration_catalog_and_schema_range():
    assert "product-19" in ENGINE_REGISTRY
    assert get_product_by_id("product-19")["name"]=="Hospital Procurement Intelligence"
    assert ProductRunFromDatasetVersionRequest(product_id="product-19",workspace_id=1,dataset_version_id=1).product_id=="product-19"

def test_procurement_math_and_po_contract_reduction():
    ss=safety_stock(10,14,1.65); assert ss>0
    assert reorder_point(100,14,ss)>1400
    assert net_procurement_requirement(2000,100,500,200,300)==1100

def test_product_run_standard_contract_and_missing_data_guardrail():
    out=run_product_engine("product-19",ROWS,{"filters":{}})
    for key in ("metrics","evidence","warnings","confidence","trust","visualizations"): assert key in out
    assert out["metrics"]["items_analyzed"]==2
    missing=run_product_engine("product-19",[{"product":"X","ordered_quantity":100}],{"filters":{}})
    assert missing["metrics"].get("items_analyzed") is None
    assert any("consumption" in w.lower() for w in missing["warnings"])

def test_consumption_not_mapped_from_po_quantity():
    m=suggest_mapping(["Product","PO Quantity","Stock On Hand"])
    assert m["suggestions"].get("consumption_quantity",{}).get("column")!="PO Quantity"

def test_intent_routes_hospital_procurement():
    route=resolve_dataset_goal(["product","consumption_quantity","inventory_on_hand","lead_time_days"],"build hospital procurement plan and shortage risk",persona="procurement",top_n=5)
    assert route["recommendedExercise"]["exerciseId"]=="product-19"

def test_supplier_kpis_and_buyer_tender_are_deterministic_and_no_award_decision():
    k=supplier_kpis(ROWS); assert k[0]["fill_rate_pct"]>0
    offers=[{"supplier":"A","price_score":90,"quality_score":80},{"supplier":"B","price_score":80,"quality_score":95}]
    result=buyer_tender_comparison(offers,{"price_score":60,"quality_score":40})
    assert len(result)==2 and "weighted_score" in result[0]
    assert all("award" not in str(x).lower() for x in result)

def test_existing_engine_reuse_is_exposed_when_inputs_supplied():
    inp={"filters":{"hospital_procurement":{"price_volume_scenario":{"base_price":10,"base_volume":100,"new_price":11,"new_volume":110},"tender_opportunity_rows":[{"Tender_Timing_Score":80,"Historical_Demand_Score":70,"Contract_Expiry_Score":60,"Product_Fit_Score":90,"Competitive_Gap_Score":50,"Win_Rate_Score":40,"Price_Competitiveness_Score":75}]}}}
    out=run_product_engine("product-19",ROWS,inp)
    assert "scenario_total_variance" in out["metrics"]
    assert out["hospital_procurement"]["tender_opportunity"]
    assert "commercial_finance.price_volume_analysis" in out["provenance"]["reused_engines"]
