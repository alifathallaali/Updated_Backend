import math

from app.engines.engine_registry import ENGINE_REGISTRY, run_product_engine
from app.engines.product_catalog import get_product_by_id
from app.engines.intent_resolver import resolve_dataset_goal
from app.reports.export_parity import prepare_export_output
from app.reports.pdf_report import build_decision_brief_pdf
from app.reports.pptx_report import build_decision_brief_pptx
from src.engines.heor_market_access.heor_decision_engine import run_heor_market_access_decision
from app.engines.heor_adapters.grounding import heor_grounding_requirement

ROWS=[
    {"period":"2026-01","sales_value":1000.0,"sales_units":10,"product":"A"},
    {"period":"2026-02","sales_value":1200.0,"sales_units":12,"product":"A"},
]

HEOR={
    "product":{"name":"Product A","cost":10000,"effect":0.75},
    "comparator":{"name":"Comparator","cost":7000,"effect":0.60},
    "economic_method":"CUA","willingness_to_pay":50000,"currency":"SAR",
    "patient_population":{"population":100000,"prevalence_rate":0.01,"diagnosis_rate":0.8,"treatment_rate":0.75},
    "budget_impact":{"uptake_rates":[0.10,0.20,0.30],"intervention_cost_per_patient":10000,"comparator_cost_per_patient":7000},
    "pricing_scenarios":[{"name":"Base","price":10000,"expected_volume":100,"access_probability_pct":80,"gtn_rate":0.10}],
    "market_access":{"formulary_status":"not listed","price":10000,"expected_volume":100,"access_probability_pct":80},
    "mcda":{"alternatives":[{"Option":"A","Clinical":90,"Cost":60},{"Option":"B","Clinical":80,"Cost":80}],"criteria":["Clinical","Cost"],"weights":{"Clinical":0.6,"Cost":0.4},"directions":{"Clinical":"benefit","Cost":"cost"},"method":"TOPSIS","id_column":"Option","sensitivity":True},
}

def test_orchestrator_reuses_canonical_dependencies():
    out=run_heor_market_access_decision(**HEOR)
    assert math.isclose(out["economic_evaluation"]["icer"],20000,rel_tol=1e-12)
    assert out["patient_flow"]["Treated_Patients"] == 600
    assert out["budget_impact"]["cumulative_budget_impact"] > 0
    assert out["market_access"]["barrier"] == "Formulary / Listing Barrier"
    reused=set(out["decision_context"]["reused_capabilities"])
    assert "market_access.price_access_tradeoff" in reused
    assert "commercial_finance.gtn_net_price" in reused


def test_registry_catalog_and_canonical_contract():
    assert "product-18" in ENGINE_REGISTRY
    assert get_product_by_id("product-18")["readiness"]["state"] == "verified_subset"
    out=run_product_engine("product-18",ROWS,{"filters":{"heor":HEOR}})
    assert math.isclose(out["metrics"]["icer"],20000,rel_tol=1e-12)
    assert out["evidence"]
    assert out["confidence"]["score"] >= 0.5
    assert out["trust"]["rawRowsSentToLLM"] is False
    assert out["heor"]["mcda"]["results"]


def test_missing_heor_inputs_are_not_inferred():
    out=run_product_engine("product-18",ROWS,{"filters":{}})
    assert out["metrics"].get("icer") is None
    assert any("never inferred" in w for w in out["warnings"])


def test_intent_resolution_exposes_heor():
    route=resolve_dataset_goal(["period","sales_value","sales_units","product"],"Calculate ICER and budget impact for this market access decision")
    assert route["intent"] == "decide"
    assert route["recommendedExercise"]["exerciseId"] == "product-18"


def test_visualization_and_report_payloads():
    out=run_product_engine("product-18",ROWS,{"filters":{"heor":HEOR}})
    chart_ids={c["chartId"] for c in out["visualizations"]}
    assert "heor-value" in chart_ids
    assert "heor-budget" in chart_ids
    export=prepare_export_output(out)
    pdf=build_decision_brief_pdf("product-18",out["status"],export)
    pptx=build_decision_brief_pptx("product-18",out["status"],export)
    assert pdf[:4] == b"%PDF"
    assert pptx[:2] == b"PK"


def test_copilot_heor_grounding_requires_explicit_assumptions():
    rec={"exerciseId":"product-18","state":"ready"}
    requirement=heor_grounding_requirement(rec,{})
    assert requirement["status"]=="PARTIAL"
    assert requirement["requiresStructuredInputs"] is True
    assert heor_grounding_requirement(rec,{"heor":HEOR}) is None
