"""PharmaLens presentation-only visualization service.

Charts are built from governed rows and/or metrics already returned by engines.
No recommendation, forecast, launch score, or commercial KPI is recomputed here.
"""
from collections import defaultdict
from typing import Any
from .chart_spec import chart_spec
from .chart_priority import prioritize_charts
from .chart_quality import apply_chart_quality
from .chart_adaptation import adapt_charts

def _num(row: dict, *keys: str) -> float:
    for key in keys:
        try:
            value=row.get(key)
            if value is not None and str(value).strip()!="": return float(value)
        except (TypeError,ValueError): pass
    return 0.0

def _text(row: dict,*keys:str)->str:
    for key in keys:
        value=row.get(key)
        if value is not None and str(value).strip(): return str(value).strip()
    return "Unknown"

def _period(row:dict)->str:
    return _text(row,"period","period_month","month","calendar_month","year")

def _trend(rows:list[dict],value_keys=("sales_value","lc_value","salesValue","value"))->list[dict]:
    g=defaultdict(float)
    for row in rows:g[_period(row)]+=_num(row,*value_keys)
    return [{"period":k,"value":v} for k,v in sorted(g.items()) if k!="Unknown"]

def _ranking(rows:list[dict],keys:tuple[str,...],limit:int=10)->list[dict]:
    g=defaultdict(float)
    for row in rows:g[_text(row,*keys)]+=_num(row,"sales_value","lc_value","salesValue","value")
    return [{"category":k,"value":v} for k,v in sorted(g.items(),key=lambda x:x[1],reverse=True)[:limit] if k!="Unknown"]

def _metric_chart(result:dict,chart_id:str,title:str,keys:list[tuple[str,str]],role="actual")->list[dict]:
    metrics=result.get("metrics") or {}
    data=[]
    for label,key in keys:
        value=metrics.get(key)
        if isinstance(value,(int,float)):data.append({"metric":label,"value":value})
    if not data:return []
    return [chart_spec(chart_id=chart_id,chart_type="bar",title=title,x_key="metric",
        series=[{"dataKey":"value","label":"Value","role":role,"valueFormat":"compact"}],data=data)]

def _market_pack(rows:list[dict],result:dict)->list[dict]:
    charts=[];trend=_trend(rows);brands=_ranking(rows,("brand_name","brand","product"));companies=_ranking(rows,("corporation","manufacturer","company"))
    if trend:charts.append(chart_spec(chart_id="market-trend",chart_type="line",title="Market value trend",x_key="period",series=[{"dataKey":"value","label":"Sales value","role":"market","valueFormat":"compact"}],data=trend))
    if brands:charts.append(chart_spec(chart_id="brand-ranking",chart_type="bar",title="Top brands",x_key="category",layout="vertical",series=[{"dataKey":"value","label":"Sales value","role":"brand","valueFormat":"compact"}],data=brands))
    if companies:charts.append(chart_spec(chart_id="company-ranking",chart_type="bar",title="Top manufacturers",x_key="category",layout="vertical",series=[{"dataKey":"value","label":"Sales value","role":"market","valueFormat":"compact"}],data=companies))
    return charts

def _company_pack(rows,result):
    return _market_pack(rows,result)[0:1]+_metric_chart(result,"company-kpis","Company portfolio snapshot",[("Top company value","top_company_sales_value"),("Brands","top_company_brand_count"),("Therapeutic classes","top_company_therapeutic_class_count")],"market")

def _molecule_pack(rows,result):
    return _metric_chart(result,"molecule-kpis","Molecule intelligence",[("Top molecule value","top_molecule_sales_value"),("Share %","top_molecule_share_pct"),("Brands","top_molecule_brand_count"),("Manufacturers","top_molecule_manufacturer_count")],"brand")+_market_pack(rows,result)[:1]

def _product_pack(rows,result):
    return _metric_chart(result,"product-kpis","Product performance",[("Top product value","top_product_sales_value"),("Average price","average_price"),("Products","product_count")],"brand")+_market_pack(rows,result)[:1]

def _share_pack(rows,result):
    return _metric_chart(result,"share-leaders","Market share leaders",[("Brand share %","leading_brand_share_pct"),("Manufacturer share %","leading_manufacturer_share_pct"),("Class share %","leading_therapeutic_class_share_pct")],"market")+_market_pack(rows,result)[:2]

def _forecast_pack(rows,result):
    charts=_market_pack(rows,result)[:1]
    charts+=_metric_chart(result,"forecast-output","Forecast output",[("Baseline forecast units","baseline_forecast_units"),("Baseline period units","baseline_period_units"),("Historical units","historical_units")],"forecast")
    charts+=_metric_chart(result,"forecast-growth","Forecast diagnostics",[("MoM growth %","latest_mom_growth_pct"),("YoY growth %","latest_yoy_growth_pct")],"forecast")
    return charts

def _launch_pack(rows,result):
    return _metric_chart(result,"launch-success","Launch success",[("Success rate %","success_rate_pct"),("High risk products","high_risk_products"),("Top success score","top_success_score"),("Top risk score","top_risk_score")],"opportunity")+_market_pack(rows,result)[:1]

def _scenario_pack(rows,result):
    return _metric_chart(result,"scenario-value","Scenario value comparison",[("Baseline value","baseline_market_value"),("Top scenario value","top_scenario_projected_value"),("Incremental revenue","top_scenario_incremental_revenue")],"forecast")

def _portfolio_pack(rows,result):
    return _metric_chart(result,"portfolio-structure","Portfolio structure",[("Products","products"),("Corporations","corporations")],"brand")+_market_pack(rows,result)[:1]

def _demand_pack(rows,result):
    charts=_metric_chart(result,"demand-plan","Demand planning",[("Demand units","total_demand_units"),("Products","product_count"),("Planning horizon","planning_horizon_periods")],"forecast")
    trend=_trend(rows,("sales_units","units"))
    if trend:charts.append(chart_spec(chart_id="demand-trend",chart_type="line",title="Observed demand trend",x_key="period",series=[{"dataKey":"value","label":"Units","role":"actual","valueFormat":"compact"}],data=trend))
    return charts

def _supply_pack(rows,result):
    trend=_trend(rows,("sales_units","units"))
    charts=_metric_chart(result,"supply-plan","Supply planning",[("Demand units","demand_units"),("Products","products"),("Planning periods","planning_periods")],"target")
    if trend:charts.append(chart_spec(chart_id="supply-demand-trend",chart_type="line",title="Observed demand for supply planning",x_key="period",series=[{"dataKey":"value","label":"Units","role":"actual","valueFormat":"compact"}],data=trend))
    return charts

def _inventory_pack(rows,result):
    return _metric_chart(result,"inventory-readiness","Inventory optimization readiness",[("Demand units","demand_units"),("Products","product_count"),("Service target %","service_level_target_pct")],"target")

def _sfe_pack(rows,result):
    return _metric_chart(result,"field-force-performance","Field force performance",[("Achievement %","achievement_pct"),("Reach %","reach_pct"),("Frequency compliance %","frequency_compliance_pct"),("Plan adherence %","plan_adherence_pct"),("Territories","territories"),("Sales reps","sales_reps")],"opportunity")

def _review_pack(rows,result):
    return _metric_chart(result,"business-review","Business review snapshot",[("Sales value","sales_value"),("Periods","periods"),("Action items","action_items")],"actual")+_market_pack(rows,result)[:1]

def _heor_pack(rows,result):
    charts=[]
    charts+=_metric_chart(result,"heor-value","HEOR value evidence",[("Incremental cost","incremental_cost"),("Incremental effect","incremental_effect"),("ICER","icer"),("Incremental NMB","incremental_nmb")],"opportunity")
    charts+=_metric_chart(result,"heor-budget","Budget impact",[("Cumulative budget impact","cumulative_budget_impact"),("Discounted budget impact","discounted_cumulative_budget_impact"),("Treated patients","treated_patients")],"forecast")
    return charts

def _consumer_health_pack(rows,result):
    charts=_metric_chart(result,"consumer-health-kpis","Consumer Health category intelligence",[("Categories","categories_analyzed"),("SKUs","skus_analyzed"),("Median price","median_price"),("Review candidates","rationalization_review_candidates")],"opportunity")
    charts+=_market_pack(rows,result)[:2]
    return charts

def _hospital_procurement_pack(rows,result):
    return _metric_chart(result,"hospital-procurement-kpis","Hospital procurement intelligence",[("Consumption","total_consumption_quantity"),("Net requirement","net_procurement_requirement"),("Projected spend","projected_procurement_spend"),("Shortage risk items","shortage_risk_items"),("Suppliers","supplier_count")],"target")

PACKS={
"product-01":_market_pack,"product-02":_company_pack,"product-03":_molecule_pack,"product-04":_product_pack,
"product-05":_share_pack,"product-06":_forecast_pack,"product-07":_launch_pack,"product-08":_scenario_pack,
"product-09":_portfolio_pack,"product-10":_demand_pack,"product-11":_supply_pack,"product-12":_inventory_pack,
"product-13":_sfe_pack,"product-14":_review_pack,"product-15":_market_pack,"product-16":_market_pack,"product-17":_market_pack,"product-18":_heor_pack,"product-19":_hospital_procurement_pack,"product-20":_consumer_health_pack,
}

def build_visualizations(product_id:str,rows:list[dict],result:dict)->list[dict]:
    if not rows:return []
    builder=PACKS.get(product_id)
    if builder:
        charts=builder(rows,result)
        try:
            from ..engines.exercise_manifest import get_exercise_manifest
            manifest=get_exercise_manifest(product_id)
            if manifest:
                return adapt_charts(apply_chart_quality(prioritize_charts(charts,manifest.family,list(manifest.chart_patterns)))[0])
        except Exception:
            pass
        return charts
    # Unknown/future exercises use the reusable family resolver.
    return build_exercise_visualizations(product_id, rows, result)

# Generic resolver for future exercise families. This allows a large exercise
# catalog to reuse governed visual patterns instead of creating one renderer per exercise.
def build_exercise_visualizations(exercise_id: str, rows: list[dict], result: dict, *, name: str = "", domain: str = "") -> list[dict]:
    from .exercise_profiles import resolve_profile
    if not rows:
        return []
    family, profile = resolve_profile(exercise_id, name=name, domain=domain)
    # Preserve hand-tuned packs where they exist.
    if exercise_id in PACKS:
        return PACKS[exercise_id](rows, result)

    charts: list[dict] = []
    role = profile["role"]
    for pattern in profile["patterns"]:
        if pattern == "metrics":
            numeric = [(k.replace("_", " ").title(), k) for k, v in (result.get("metrics") or {}).items()
                       if isinstance(v, (int, float))][:8]
            charts += _metric_chart(result, f"{exercise_id}-metrics", "Key decision metrics", numeric, role)
        elif pattern == "trend":
            data = _trend(rows)
            if data:
                charts.append(chart_spec(chart_id=f"{exercise_id}-trend", chart_type="line", title="Performance trend",
                    x_key="period", series=[{"dataKey":"value","label":"Value","role":role,"valueFormat":"compact"}], data=data))
        elif pattern == "unit_trend":
            data = _trend(rows, ("sales_units", "units", "demand_units", "quantity"))
            if data:
                charts.append(chart_spec(chart_id=f"{exercise_id}-unit-trend", chart_type="line", title="Volume trend",
                    x_key="period", series=[{"dataKey":"value","label":"Units","role":role,"valueFormat":"compact"}], data=data))
        elif pattern == "brand_ranking":
            data = _ranking(rows, ("brand_name", "brand", "product"))
            if data:
                charts.append(chart_spec(chart_id=f"{exercise_id}-brand-ranking", chart_type="bar", title="Brand ranking",
                    x_key="category", layout="vertical", series=[{"dataKey":"value","label":"Value","role":role,"valueFormat":"compact"}], data=data))
        elif pattern == "company_ranking":
            data = _ranking(rows, ("corporation", "manufacturer", "company"))
            if data:
                charts.append(chart_spec(chart_id=f"{exercise_id}-company-ranking", chart_type="bar", title="Company ranking",
                    x_key="category", layout="vertical", series=[{"dataKey":"value","label":"Value","role":role,"valueFormat":"compact"}], data=data))
    return adapt_charts(apply_chart_quality(prioritize_charts(charts[:6], family, list(profile["patterns"])))[0])
