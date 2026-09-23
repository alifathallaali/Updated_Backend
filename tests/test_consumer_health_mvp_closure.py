from app.engines.engine_registry import ENGINE_REGISTRY, run_product_engine
from app.engines.exercise_manifest import EXERCISE_MANIFESTS
from app.engines.product_catalog import get_product_by_id
from app.engines.intent_resolver import resolve_dataset_goal
from app.engines.data_compatibility import assess_exercise_compatibility
from app.reports.export_parity import prepare_export_output
from app.reports.pdf_report import build_decision_brief_pdf
from app.reports.pptx_report import build_decision_brief_pptx

ROWS=[
 {"period":"2026-01","category":"VMS","subcategory":"Collagen","product":"Glow A","sku":"A30","pack_size":"30 sachets","manufacturer":"Co A","sales_value":1000,"sales_units":100,"price":50,"channel":"Pharmacy","retailer":"Chain A","numeric_distribution":20},
 {"period":"2026-02","category":"VMS","subcategory":"Collagen","product":"Glow A","sku":"A30","pack_size":"30 sachets","manufacturer":"Co A","sales_value":1200,"sales_units":110,"price":52,"channel":"Pharmacy","retailer":"Chain A","numeric_distribution":22},
 {"period":"2026-01","category":"VMS","subcategory":"Vitamin D","product":"Vit D B","sku":"B60","pack_size":"60 tablets","manufacturer":"Co B","sales_value":500,"sales_units":80,"price":30,"channel":"Ecommerce","retailer":"Online B","numeric_distribution":10},
 {"period":"2026-02","category":"VMS","subcategory":"Vitamin D","product":"Vit D B","sku":"B60","pack_size":"60 tablets","manufacturer":"Co B","sales_value":400,"sales_units":70,"price":29,"channel":"Ecommerce","retailer":"Online B","numeric_distribution":9},
]

def test_single_registration_and_catalog():
    assert "product-20" in ENGINE_REGISTRY
    assert sum(1 for m in EXERCISE_MANIFESTS if m.id=="product-20")==1
    assert get_product_by_id("product-20")["name"]=="Consumer Health Intelligence"

def test_intent_resolution():
    route=resolve_dataset_goal(list(ROWS[0]),"analyze consumer health category management assortment and price bands")
    assert route["recommendedExercise"]["exerciseId"]=="product-20"

def test_compatibility_aliases():
    out=assess_exercise_compatibility("product-20",["market_category","product_name","selling_value","retail_price","retail_chain"])
    assert out["state"]=="ready"

def test_reuses_market_company_product_and_category_primitives():
    out=run_product_engine("product-20",ROWS,{"filters":{}})
    assert set(["market","company","product"]).issubset(out["metrics"]["reused_capabilities"])
    assert out["metrics"]["categories_analyzed"]==1
    assert out["metrics"]["skus_analyzed"]==2
    assert out["categoryManagement"]["sku_contribution"]

def test_price_bands_deterministic():
    a=run_product_engine("product-20",ROWS,{"filters":{}})["categoryManagement"]["price_architecture"]
    b=run_product_engine("product-20",ROWS,{"filters":{}})["categoryManagement"]["price_architecture"]
    assert a==b and a["method"]=="dataset-relative median bands"

def test_productivity_and_distribution_guardrails():
    ok=run_product_engine("product-20",ROWS,{"filters":{}})
    assert "sku_productivity" in ok["categoryManagement"]
    missing=[{k:v for k,v in r.items() if k!="numeric_distribution"} for r in ROWS]
    out=run_product_engine("product-20",missing,{"filters":{}})
    assert "sku_productivity" not in out["categoryManagement"]
    assert any("SKU productivity omitted" in w for w in out["warnings"])
    assert any("Distribution-gap analysis omitted" in w for w in out["warnings"])

def test_assortment_guardrail():
    missing=[{k:v for k,v in r.items() if k not in {"retailer","channel"}} for r in ROWS]
    out=run_product_engine("product-20",missing,{"filters":{}})
    assert "assortment" not in out["categoryManagement"]
    assert any("Assortment analysis omitted" in w for w in out["warnings"])

def test_promotion_consumer_ecommerce_guardrails():
    offline=[{**r,"channel":"Pharmacy"} for r in ROWS]
    out=run_product_engine("product-20",offline,{"filters":{}})
    assert any("Promotion effectiveness omitted" in w for w in out["warnings"])
    assert any("Consumer insights omitted" in w for w in out["warnings"])
    assert any("E-commerce performance omitted" in w for w in out["warnings"])

def test_market_share_denominator_guardrail():
    rows=[{"category":"VMS","product":"A","sku":"A","price":10}]
    out=run_product_engine("product-20",rows,{"filters":{}})
    assert any("market-share outputs omitted" in w for w in out["warnings"])
    assert "sku_contribution" not in out["categoryManagement"]

def test_historical_forecast_separation():
    out=run_product_engine("product-20",ROWS,{"filters":{}})
    assert out["metrics"]["historical_observations_only"] is True
    assert "forecast" in out["metrics"]["reused_capabilities"]
    assert out["governance"]["forecastLabeling"]

def test_rationalization_is_review_only():
    out=run_product_engine("product-20",ROWS,{"filters":{}})
    candidates=out["categoryManagement"]["rationalization_candidates"]
    assert candidates and all(x["status"]=="review_candidate" for x in candidates)

def test_trust_evidence_warning_confidence_and_visualization():
    out=run_product_engine("product-20",ROWS,{"filters":{}})
    assert out["evidence"] and out["warnings"] and out["confidence"]
    assert out["trust"]["rawRowsSentToLLM"] is False
    assert out["visualizations"]

def test_reports_reuse_standard_export_pipeline():
    out=run_product_engine("product-20",ROWS,{"filters":{}})
    export=prepare_export_output(out)
    assert build_decision_brief_pdf("product-20",out["status"],export)
    assert build_decision_brief_pptx("product-20",out["status"],export)

def test_grounded_copilot_contract_available_through_intent_and_product_run():
    route=resolve_dataset_goal(list(ROWS[0]),"consumer health SKU assortment category opportunity")
    out=run_product_engine(route["recommendedExercise"]["exerciseId"],ROWS,{"filters":{}})
    assert out["productId"]=="product-20"
    assert out["trust"]["rawRowsSentToLLM"] is False
