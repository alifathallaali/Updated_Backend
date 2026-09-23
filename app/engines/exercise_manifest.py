"""Declarative Exercise Manifest for PharmaLens AI.

The manifest describes orchestration and presentation metadata. It never
implements analytics. This allows the exercise catalog to scale without
duplicating frontend or renderer logic.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Literal

Readiness = Literal["verified_subset", "foundation_only", "additional_inputs", "planned"]

@dataclass(frozen=True)
class ExerciseManifest:
    id: str
    name: str
    domain: str
    family: str
    personas: tuple[str, ...]
    required_inputs: tuple[str, ...] = ()
    optional_inputs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ("canonical_sales",)
    kpis: tuple[str, ...] = ()
    chart_patterns: tuple[str, ...] = ()
    table: str = "generic_evidence"
    report_section: str = "Analysis"
    readiness: Readiness = "foundation_only"
    source: str = ""
    tags: tuple[str, ...] = ()

    def to_api(self) -> dict:
        data = asdict(self)
        data["requiredInputs"] = data.pop("required_inputs")
        data["optionalInputs"] = data.pop("optional_inputs")
        data["reportSection"] = data.pop("report_section")
        data["chartPatterns"] = data.pop("chart_patterns")
        data["status"] = "production" if self.readiness == "verified_subset" else "in_progress"
        data["readiness"] = {"state": self.readiness, "source": self.source}
        return data

def _m(id,name,domain,family,personas,required=(),kpis=(),patterns=(),table="generic_evidence",
       section="Analysis",readiness="foundation_only",source="",tags=(),optional=()):
    return ExerciseManifest(id,name,domain,family,tuple(personas),tuple(required),tuple(optional),
        ("canonical_sales",),tuple(kpis),tuple(patterns),table,section,readiness,source,tuple(tags))

EXERCISE_MANIFESTS = [
_m("product-01","Market Intelligence","explore","market",("brand_manager","commercial_manager","analyst"),
   ("period","sales_value"),("total_sales_value","total_sales_units","brands","manufacturers"),
   ("trend","ranking","share"),"market_leaders","Market overview","verified_subset","market_intelligence.py",("market","performance")),
_m("product-02","Company Intelligence","explore","company",("commercial_manager","business_development","analyst"),
   ("manufacturer","sales_value"),("company_count","top_company_sales_value","top_company_brand_count","top_company_therapeutic_class_count"),
   ("trend","ranking","portfolio"),"company_leaders","Company performance","verified_subset","company.py",("company","competition")),
_m("product-03","Molecule Intelligence","explore","molecule",("brand_manager","medical_affairs","analyst"),
   ("active_ingredient","sales_value"),("top_molecule_sales_value","top_molecule_share_pct","top_molecule_brand_count","top_molecule_manufacturer_count"),
   ("trend","ranking","share"),"molecule_leaders","Molecule landscape","verified_subset","03_Molecule_Intelligence.ipynb",("molecule","competition")),
_m("product-04","Product Performance","analyze","product",("brand_manager","commercial_manager"),
   ("product","sales_value"),("top_product_sales_value","average_price","product_count"),("trend","ranking","variance"),
   "product_leaders","Product performance","foundation_only","Product foundation adapter",("product","performance")),
_m("product-05","Market Share & Growth","analyze","market",("brand_manager","commercial_manager","analyst"),
   ("brand","sales_value","period"),("leading_brand_share_pct","leading_manufacturer_share_pct","leading_therapeutic_class_share_pct"),
   ("share","trend","ranking"),"share_leaders","Share and growth","verified_subset","market_intelligence.py",("share","growth")),
_m("product-06","Forecasting","strategize","forecast",("demand_planner","brand_manager","finance"),
   ("period","sales_units"),("baseline_forecast_units","baseline_period_units","latest_mom_growth_pct","latest_yoy_growth_pct"),
   ("actual_vs_forecast","trend","variance"),"forecast_diagnostics","Forecast","verified_subset","02_Advanced_pharmaceutical_Forecasting.ipynb",("forecast","planning")),
_m("product-07","Launch Success","strategize","launch",("brand_manager","launch_team","commercial_manager"),
   ("product","period","sales_value"),("success_rate_pct","high_risk_products","top_success_score","top_risk_score"),
   ("score","risk_matrix","trend"),"launch_risk","Launch readiness","verified_subset","launch.py",("launch","risk")),
_m("product-08","Scenario Planning","strategize","scenario",("commercial_manager","finance","strategy"),
   ("period","sales_value"),("baseline_market_value","top_scenario_projected_value","top_scenario_incremental_revenue"),
   ("scenario_comparison","waterfall","trend"),"scenario_comparison","Scenario planning","verified_subset","scenario.py",("scenario","strategy")),
_m("product-09","Portfolio Strategy","strategize","product",("portfolio_manager","commercial_manager"),
   ("product","manufacturer","sales_value"),("products","corporations"),("matrix","ranking","share"),
   "portfolio","Portfolio strategy","foundation_only","recommendation.py placeholder",("portfolio","strategy")),
_m("product-10","Demand Planning","execute","supply",("demand_planner","supply_chain"),
   ("product","period","sales_units"),("total_demand_units","product_count","planning_horizon_periods"),
   ("trend","actual_vs_plan","variance"),"demand_plan","Demand plan","foundation_only","Demand foundation adapter",("demand","planning")),
_m("product-11","Supply Planning","execute","supply",("supply_planner","procurement"),
   ("product","period","sales_units"),("demand_units","products","planning_periods"),("trend","coverage","variance"),
   "supply_plan","Supply plan","foundation_only","Supply foundation adapter",("supply","planning")),
_m("product-12","Inventory Optimization","execute","inventory",("supply_chain","warehouse","procurement"),
   ("product","sales_units"),("demand_units","product_count","service_level_target_pct"),("stock_cover","risk_matrix","ranking"),
   "inventory_readiness","Inventory","additional_inputs","Requires inventory, lead-time and service-level evidence",("inventory","optimization"),
   ("inventory_on_hand","lead_time","service_level")),
_m("product-13","Field Force Planner & Sales Force Effectiveness","sales","sales",("sales_manager","field_force","first_line_manager","commercial_excellence"),
   ("territory","sales_rep"),("territories","sales_reps","observed_records","target","actual","achievement_pct","reach_pct","average_frequency","frequency_compliance_pct","plan_adherence_pct"),("achievement","ranking","coverage","variance","priority_matrix"),
   "field_force_plan","Field force planning & execution","verified_subset","app/engines/field_force_adapters + existing target/forecast/recommendation/scenario/finance engines",("sales","sfe","field force","med rep","territory","coverage","frequency","achievement","target","call plan","hcp priority"),
   ("calls","target","actual","hcp","hco","potential","planned_calls","required_frequency","capacity","period","product")),
_m("product-14","Business Review & Action Plan","sales","sales",("commercial_manager","brand_manager","sales_manager"),
   ("period","sales_value"),("sales_value","periods","action_items"),("scorecard","trend","variance"),
   "business_review","Business review","foundation_only","Enterprise wrapper foundation",("review","action_plan")),
_m("product-15","Commercial Recommendations Engine","decide","sales",("commercial_manager","brand_manager"),
   ("product","sales_value","period"),(),("priority_matrix","ranking"),"recommendations","Commercial recommendations",
   "foundation_only","commercial_adapters.py",("recommendation","decision")),
_m("product-16","Go-To-Market (GTM) Analytics","decide","market_access",("commercial_manager","market_access","business_development"),
   ("product","period","sales_value"),(),("channel_mix","coverage","priority_matrix"),"gtm_actions","Go-to-market",
   "foundation_only","commercial_adapters.py",("gtm","channel")),
_m("product-17","Commercial Finance Engine","decide","finance",("finance","commercial_manager"),
   ("period","sales_value"),(),("variance","waterfall","trend"),"financial_variance","Commercial finance",
   "foundation_only","commercial_adapters.py",("finance","budget"),("budget","target","cost")),
_m("product-18","HEOR & Market Access Decision Engine","decide","market_access",("market_access","health_economics","medical_affairs","finance","commercial_manager"),
   (),("incremental_cost","incremental_effect","icer","incremental_nmb","cumulative_budget_impact"),
   ("metrics","scenario_comparison","priority_matrix"),"heor_decision_matrix","HEOR & value evidence",
   "verified_subset","src/engines/heor_market_access + app/engines/heor_adapters",
   ("heor","health economics","cost effectiveness","icer","qaly","budget impact","mcda","hta","market access")),
_m("product-19","Hospital Procurement Intelligence","execute","supply",("supply_chain","procurement","hospital_manager","hospital_pharmacy"),
   ("product","consumption_quantity"),("items_analyzed","total_consumption_quantity","net_procurement_requirement","projected_procurement_spend","shortage_risk_items"),
   ("metrics","coverage","risk_matrix","ranking"),"hospital_procurement_plan","Hospital procurement","verified_subset",
   "src/engines/hospital_procurement + app/engines/hospital_procurement_adapters",
   ("hospital","procurement","supply chain","stock","inventory","reorder","purchase order","supplier","tender"),
   ("inventory_on_hand","lead_time_days","open_po_quantity","contract_covered_quantity","expected_unit_cost","budget","supplier")),
_m("product-20","Consumer Health Intelligence","analyze","market",("category_manager","brand_manager","commercial_manager","analyst"),
   ("category","product","sales_value"),("categories_analyzed","skus_analyzed","median_price","rationalization_review_candidates"),
   ("trend","ranking","share","price"),"category_performance","Consumer Health & category management","verified_subset",
   "app/engines/consumer_health_adapters + canonical PharmaLens engines",
   ("consumer health","otc","supplements","vitamins","cosmetics","beauty","personal care","wellness","category management","sku","assortment","retailer","price band"),
   ("subcategory","sku","pack","channel","retailer","price","distribution","promotion","consumer_segment","ecommerce","period","sales_units")),
]
MANIFEST_BY_ID={m.id:m for m in EXERCISE_MANIFESTS}

def get_exercise_manifest(exercise_id: str):
    return MANIFEST_BY_ID.get(exercise_id)

def list_exercise_manifests():
    return [m.to_api() for m in EXERCISE_MANIFESTS]
