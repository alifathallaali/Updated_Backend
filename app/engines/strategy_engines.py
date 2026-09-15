import re

from ._helpers import build_output, median


def _value(row: dict, *keys: str) -> float:
    for key in keys:
        raw = row.get(key)
        try:
            numeric = float(raw)
            if numeric == numeric:  # not NaN
                return numeric
        except (TypeError, ValueError):
            continue
    return 0.0


def _label(row: dict, *keys: str) -> str:
    for key in keys:
        raw = row.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return "Unknown"


def run_forecasting(rows: list[dict], input_: dict) -> dict:
    units = [u for u in (_value(r, "sales_units", "units") for r in rows) if u >= 0]
    total = sum(units)
    average = total / len(units) if units else 0
    filters = input_.get("filters") or {}
    try:
        requested_horizon = float(filters.get("horizon_periods"))
    except (TypeError, ValueError):
        requested_horizon = None
    horizon_periods = int(requested_horizon) if requested_horizon and 1 <= requested_horizon <= 24 else 3

    monthly: dict[str, float] = {}
    for row in rows:
        period = _label(row, "period", "month", "calendar_month")
        if period != "Unknown":
            monthly[period] = monthly.get(period, 0) + _value(row, "sales_value", "lc_value", "salesValue", "value")
    period_values = sorted(monthly.items())
    latest = period_values[-1] if period_values else None
    previous = period_values[-2] if len(period_values) >= 2 else None
    prior_year = period_values[-13] if len(period_values) >= 13 else None

    def pct_change(current, prior):
        if current is None or prior is None or prior[1] == 0:
            return None
        return ((current[1] / prior[1]) - 1) * 100

    annual: dict[str, float] = {}
    for period, value in period_values:
        match = re.search(r"\d{4}", period)
        if match:
            annual[match.group(0)] = annual.get(match.group(0), 0) + value

    warnings = (
        ["This is a transparent historical-average run-rate estimate; monthly growth is descriptive and not a notebook-grade time-series forecast."]
        if units else ["No sales units were available for forecasting."]
    )
    return build_output(
        "product-06",
        "Historical forecasting diagnostics with monthly growth, annual totals, and an explicit run-rate estimate.",
        {
            "observations": len(units), "historical_units": total, "baseline_period_units": average,
            "forecast_horizon_periods": horizon_periods, "forecast_method": "historical_average",
            "baseline_forecast_units": average * horizon_periods, "historical_periods": len(period_values),
            "latest_sales_value": latest[1] if latest else None,
            "latest_mom_growth_pct": pct_change(latest, previous), "latest_yoy_growth_pct": pct_change(latest, prior_year),
            "annual_periods": len(annual),
        },
        [
            {"field": "sales_units", "value": total, "source": "canonical"},
            {"field": "latest_sales_value", "value": latest[1] if latest else None, "source": "02_Advanced_pharmaceutical_Forecasting.ipynb / canonical"},
            {"field": "latest_mom_growth_pct", "value": pct_change(latest, previous), "source": "02_Advanced_pharmaceutical_Forecasting.ipynb / canonical"},
        ],
        warnings,
    )


def _launch_month_rank(raw) -> float:
    match = re.search(r"(\d{4})[-/](\d{1,2})", str(raw or "").strip())
    return int(match.group(1)) * 12 + int(match.group(2)) if match else float("nan")


def run_launch_success(rows: list[dict], _input: dict) -> dict:
    product_rows: dict[str, dict] = {}
    for row in rows:
        launch_rank = _launch_month_rank(row.get("product_launch") or row.get("launch_date"))
        period_rank = _launch_month_rank(row.get("period") or row.get("month"))
        if launch_rank != launch_rank or period_rank != period_rank:  # NaN check
            continue
        age = max(0, period_rank - launch_rank)
        parts = [row.get("corporation") or row.get("manufacturer"), row.get("brand_name") or row.get("product"), row.get("strength"), row.get("pack")]
        pid = " | ".join(str(p or "").strip() for p in parts)
        current = product_rows.setdefault(pid, {"label": str(row.get("brand_name") or row.get("product") or "Unknown"), "records": []})
        current["records"].append({"age": age, "value": _value(row, "sales_value", "lc_value", "value"), "units": _value(row, "sales_units", "units")})

    products = []
    for pid, data in product_rows.items():
        ordered = sorted(data["records"], key=lambda r: r["age"])

        def sum_window(max_age, key):
            return sum(r[key] for r in ordered if r["age"] <= max_age)

        first3, first6, first12 = sum_window(2, "value"), sum_window(5, "value"), sum_window(11, "value")
        peak_record = max(ordered, key=lambda r: r["value"]) if ordered else {"value": 0, "age": 0}
        first_value = ordered[0]["value"] if ordered else 0
        latest_value = ordered[-1]["value"] if ordered else 0
        value_growth = ((latest_value / first_value) - 1) * 100 if first_value > 0 else 0
        products.append({
            "id": pid, "label": data["label"], "first3": first3, "first6": first6, "first12": first12,
            "peak": peak_record["value"], "timeToPeak": peak_record["age"], "firstValue": first_value, "latestValue": latest_value,
            "successScore": 0, "riskScore": 1 if value_growth < 0 else 0,
        })

    first3_median = median([p["first3"] for p in products])
    first6_median = median([p["first6"] for p in products])
    first12_median = median([p["first12"] for p in products])
    peak_median = median([p["peak"] for p in products])
    time_to_peak_median = median([p["timeToPeak"] for p in products])
    for p in products:
        p["successScore"] = int(p["first3"] >= first3_median) + int(p["first6"] >= first6_median) + int(p["first12"] >= first12_median) + int(p["peak"] >= peak_median)
        p["riskScore"] += int(p["first3"] < first3_median) + int(p["first6"] < first6_median) + int(p["timeToPeak"] > time_to_peak_median)

    successful = sum(1 for p in products if p["successScore"] >= 3)
    top = max(products, key=lambda p: (p["successScore"], p["first12"]), default=None)
    high_risk = sum(1 for p in products if p["riskScore"] >= 3)
    success_category = (
        "Highly Successful" if top and top["successScore"] == 4 else
        "Successful" if top and top["successScore"] == 3 else
        "Moderate" if top and top["successScore"] == 2 else
        "Weak" if top and top["successScore"] == 1 else
        "Unsuccessful" if top else "Unknown"
    )
    risk_category = (
        "High Risk" if top and top["riskScore"] >= 3 else
        "Medium Risk" if top and top["riskScore"] == 2 else
        "Low Risk" if top and top["riskScore"] == 1 else
        "Minimal Risk" if top else "Unknown"
    )
    strategic = (
        "Scale / Accelerate" if success_category == "Highly Successful" and risk_category in ("Minimal Risk", "Low Risk") else
        "Invest / Expand" if success_category == "Successful" and risk_category in ("Minimal Risk", "Low Risk") else
        "Optimize" if success_category == "Moderate" and risk_category == "Medium Risk" else
        "Intervention Required" if risk_category == "High Risk" else
        "Review / Deprioritize"
    )
    warnings = (
        ["Launch scores and risk categories follow the verified launch.py benchmark rules; they are descriptive, not causal attribution."]
        if products else ["No rows with both a valid launch date and reporting period were available."]
    )
    return build_output(
        "product-07",
        "Launch Success intelligence from first 3/6/12-month performance, peak timing, growth, and benchmark scores.",
        {
            "launched_products": len(products), "success_rate_pct": (successful / len(products)) * 100 if products else 0,
            "high_risk_products": high_risk, "first_3m_value_median": first3_median, "first_6m_value_median": first6_median,
            "first_12m_value_median": first12_median, "peak_value_median": peak_median,
            "top_product": top["label"] if top else None, "top_success_score": top["successScore"] if top else None,
            "top_risk_score": top["riskScore"] if top else None, "top_success_category": success_category,
            "top_risk_category": risk_category, "top_strategic_segment": strategic,
        },
        [
            {"field": "launched_products", "value": len(products), "source": "launch.py / canonical"},
            {"field": "top_product", "value": top["label"] if top else None, "source": "launch.py / canonical"},
            {"field": "launch_success_score", "value": top["successScore"] if top else None, "source": "launch.py benchmark"},
            {"field": "launch_risk_score", "value": top["riskScore"] if top else None, "source": "launch.py benchmark"},
        ],
        warnings,
    )


VERIFIED_SCENARIOS = {
    "Base Case": {"market_growth": 0.10, "unit_growth": 0.08, "price_change": 0.02, "diagnosis_rate_change": 0, "treatment_rate_change": 0, "competition_change": 0},
    "Upside": {"market_growth": 0.15, "unit_growth": 0.12, "price_change": 0.03, "diagnosis_rate_change": 0.05, "treatment_rate_change": 0.05, "competition_change": -0.03},
    "Downside": {"market_growth": 0.05, "unit_growth": 0.03, "price_change": 0, "diagnosis_rate_change": -0.05, "treatment_rate_change": -0.05, "competition_change": 0.05},
}


def _month_key(row: dict) -> str:
    raw = row.get("period") or row.get("month") or row.get("calendar_month") or row.get("year")
    match = re.search(r"(\d{4})[-/](\d{1,2})", str(raw or "").strip())
    return f"{match.group(1)}-{match.group(2).zfill(2)}" if match else ""


def _month_rank(key: str) -> float:
    match = re.match(r"(\d{4})-(\d{2})", key)
    return int(match.group(1)) * 12 + int(match.group(2)) if match else float("nan")


def run_scenario_planning(rows: list[dict], input_: dict) -> dict:
    filters = input_.get("filters") or {}
    try:
        requested_months = float(filters.get("baseline_months"))
    except (TypeError, ValueError):
        requested_months = None
    months = int(requested_months) if requested_months and 1 <= requested_months <= 36 else 12

    valid_periods = sorted(p for p in (_month_key(r) for r in rows) if p)
    latest_period = valid_periods[-1] if valid_periods else ""
    latest_rank = _month_rank(latest_period)
    baseline_start_rank = latest_rank - months + 1 if latest_rank == latest_rank else float("nan")
    baseline_periods = {p for p in valid_periods if baseline_start_rank == baseline_start_rank and baseline_start_rank <= _month_rank(p) <= latest_rank}
    baseline_rows = [r for r in rows if _month_key(r) in baseline_periods] if latest_period else rows
    baseline_value = sum(_value(r, "sales_value", "lc_value", "value") for r in baseline_rows)
    baseline_units = sum(_value(r, "sales_units", "units") for r in baseline_rows)

    scenario_rows = []
    for name, assumptions in VERIFIED_SCENARIOS.items():
        projected_value = baseline_value * (1 + assumptions["market_growth"])
        projected_units = baseline_units * (1 + assumptions["unit_growth"])
        scenario_rows.append({"name": name, "projectedValue": projected_value, "projectedUnits": projected_units, "incrementalRevenue": projected_value - baseline_value, "assumptions": assumptions})
    top_scenario = max(scenario_rows, key=lambda s: s["incrementalRevenue"], default=None)

    grouped_brands: dict[str, float] = {}
    for row in baseline_rows:
        label = str(row.get("brand_name") or row.get("brand") or row.get("product") or "Unknown")
        grouped_brands[label] = grouped_brands.get(label, 0) + _value(row, "sales_value", "lc_value", "value")
    top_brand = max(grouped_brands.items(), key=lambda kv: kv[1], default=None)

    warnings = (
        ["Scenario projections apply verified assumption tables to the selected historical baseline; they are not causal forecasts."]
        if baseline_rows else ["No valid baseline observations were available for scenario planning."]
    )
    return build_output(
        "product-08",
        "Scenario planning using a verified historical baseline and Base Case, Upside, and Downside assumptions.",
        {
            "baseline_months": months, "baseline_periods": len(baseline_periods), "baseline_market_value": baseline_value,
            "baseline_units": baseline_units, "scenario_count": len(scenario_rows),
            "top_scenario": top_scenario["name"] if top_scenario else None,
            "top_scenario_incremental_revenue": top_scenario["incrementalRevenue"] if top_scenario else 0,
            "top_scenario_projected_value": top_scenario["projectedValue"] if top_scenario else 0,
            "top_scenario_projected_units": top_scenario["projectedUnits"] if top_scenario else 0,
            "top_brand": top_brand[0] if top_brand else None, "top_brand_baseline_value": top_brand[1] if top_brand else 0,
        },
        [
            {"field": "baseline_sales_value", "value": baseline_value, "source": "Product 12 scenario.py / canonical"},
            {"field": "baseline_sales_units", "value": baseline_units, "source": "Product 12 scenario.py / canonical"},
            {"field": "top_scenario", "value": top_scenario["name"] if top_scenario else None, "source": "verified scenario assumptions"},
            {"field": "top_brand", "value": top_brand[0] if top_brand else None, "source": "Product 12 scenario.py / canonical"},
        ],
        warnings,
    )


def run_portfolio_strategy(rows: list[dict], _input: dict) -> dict:
    products = {_label(r, "product", "brand_name") for r in rows}
    corporations = {_label(r, "corporation", "manufacturer") for r in rows}
    return build_output(
        "product-09",
        "Portfolio structure prepared for prioritization and strategic review.",
        {"products": len(products), "corporations": len(corporations)},
        [{"field": "product", "value": len(products), "source": "canonical"}, {"field": "corporation", "value": len(corporations), "source": "canonical"}],
    )


def run_demand_planning(rows: list[dict], _input: dict) -> dict:
    total_units = sum(_value(r, "sales_units", "units") for r in rows)
    product_count = len({_label(r, "product", "brand_name") for r in rows})
    return build_output(
        "product-10",
        "Demand planning baseline prepared from product-level historical unit demand.",
        {"total_demand_units": total_units, "product_count": product_count, "planning_horizon_periods": 12},
        [{"field": "sales_units", "value": total_units, "source": "canonical"}],
    )


STRATEGY_ENGINES = {
    "product-06": run_forecasting,
    "product-07": run_launch_success,
    "product-08": run_scenario_planning,
    "product-09": run_portfolio_strategy,
    "product-10": run_demand_planning,
}
