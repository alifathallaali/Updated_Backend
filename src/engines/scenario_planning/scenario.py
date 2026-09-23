# ============================================================
# PHARMALENS AI
# PROJECT 12 — SCENARIO ENGINE
# ============================================================

from pathlib import Path
import numpy as np
import pandas as pd


DEFAULT_SCENARIOS = {
    "Base Case": {
        "market_growth": 0.10,
        "unit_growth": 0.08,
        "price_change": 0.02,
        "diagnosis_rate_change": 0.00,
        "treatment_rate_change": 0.00,
        "competition_change": 0.00,
    },
    "Upside": {
        "market_growth": 0.15,
        "unit_growth": 0.12,
        "price_change": 0.03,
        "diagnosis_rate_change": 0.05,
        "treatment_rate_change": 0.05,
        "competition_change": -0.03,
    },
    "Downside": {
        "market_growth": 0.05,
        "unit_growth": 0.03,
        "price_change": 0.00,
        "diagnosis_rate_change": -0.05,
        "treatment_rate_change": -0.05,
        "competition_change": 0.05,
    },
}


CORE_COLUMNS = [
    "Brand Name",
    "Manufacturer",
    "Therapeutic Class",
    "Sales Units",
    "Sales Value",
    "Month",
]


def _project_root(project_root=None):
    if project_root is not None:
        return Path(project_root).resolve()
    return Path(__file__).resolve().parents[1]


def _find_dataset(project_root):
    root = _project_root(project_root)
    candidates = [
        root / "data" / "processed" / "cleaned_pharma_data.parquet",
        root / "data" / "processed" / "processed_data.parquet",
        root / "data" / "processed" / "pharma_data.parquet",
        root / "data" / "processed" / "market_data.parquet",
    ]
    for path in candidates:
        if path.exists():
            return path

    processed = root / "data" / "processed"
    if processed.exists():
        parquet_files = sorted(processed.glob("*.parquet"))
        if parquet_files:
            return parquet_files[0]

    raise FileNotFoundError(
        "No processed parquet dataset was found. Expected a file under "
        f"{root / 'data' / 'processed'}."
    )


def load_data(project_root=None, data_path=None):
    path = Path(data_path).resolve() if data_path else _find_dataset(project_root)
    df = pd.read_parquet(path)

    missing = [c for c in CORE_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    df = df.copy()
    df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
    df = df.dropna(subset=["Month"])

    for col in ["Sales Units", "Sales Value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "Selling Price" in df.columns:
        df["Selling Price"] = pd.to_numeric(
            df["Selling Price"], errors="coerce"
        )

    return df.sort_values("Month").reset_index(drop=True)


def calculate_baseline(df, months=12):
    if df.empty:
        raise ValueError("Dataset is empty.")

    latest_month = df["Month"].max()
    baseline_start = latest_month - pd.DateOffset(months=months - 1)

    baseline_df = df[df["Month"].between(baseline_start, latest_month)].copy()

    market_value = float(baseline_df["Sales Value"].sum())
    market_units = float(baseline_df["Sales Units"].sum())

    return {
        "baseline_df": baseline_df,
        "market_value": market_value,
        "market_units": market_units,
        "latest_month": latest_month,
        "baseline_start": baseline_start,
    }


def run_market_scenarios(df, scenarios=None, months=12):
    scenarios = scenarios or DEFAULT_SCENARIOS
    baseline = calculate_baseline(df, months=months)

    rows = []
    for name, a in scenarios.items():
        projected_value = baseline["market_value"] * (1 + a["market_growth"])
        projected_units = baseline["market_units"] * (1 + a["unit_growth"])

        rows.append({
            "Scenario": name,
            "Baseline_Market_Value": baseline["market_value"],
            "Projected_Market_Value": projected_value,
            "Market_Value_Growth_%": a["market_growth"] * 100,
            "Incremental_Revenue": projected_value - baseline["market_value"],
            "Baseline_Units": baseline["market_units"],
            "Projected_Units": projected_units,
            "Unit_Growth_%": a["unit_growth"] * 100,
            "Price_Change_%": a["price_change"] * 100,
            "Diagnosis_Rate_Change_%": a["diagnosis_rate_change"] * 100,
            "Treatment_Rate_Change_%": a["treatment_rate_change"] * 100,
            "Competition_Change_%": a["competition_change"] * 100,
        })

    return pd.DataFrame(rows)


def run_brand_scenarios(df, scenarios=None, months=12):
    scenarios = scenarios or DEFAULT_SCENARIOS
    baseline = calculate_baseline(df, months=months)
    baseline_df = baseline["baseline_df"]
    market_value = baseline["market_value"]

    group_cols = ["Brand Name", "Manufacturer", "Therapeutic Class"]
    brand = (
        baseline_df.groupby(group_cols, dropna=False, as_index=False)
        .agg(
            Baseline_Sales_Value=("Sales Value", "sum"),
            Baseline_Sales_Units=("Sales Units", "sum"),
        )
    )

    rows = []
    for name, a in scenarios.items():
        temp = brand.copy()
        market_growth = a["market_growth"]
        unit_growth = a["unit_growth"]

        temp["Scenario"] = name
        temp["Projected_Sales_Value"] = (
            temp["Baseline_Sales_Value"] * (1 + market_growth)
        )
        temp["Projected_Sales_Units"] = (
            temp["Baseline_Sales_Units"] * (1 + unit_growth)
        )
        temp["Revenue_Change"] = (
            temp["Projected_Sales_Value"]
            - temp["Baseline_Sales_Value"]
        )
        temp["Revenue_Growth_%"] = np.where(
            temp["Baseline_Sales_Value"] > 0,
            (
                temp["Projected_Sales_Value"]
                / temp["Baseline_Sales_Value"]
                - 1
            ) * 100,
            np.nan,
        )
        scenario_market = market_value * (1 + market_growth)
        temp["Projected_Market_Share_%"] = np.where(
            scenario_market > 0,
            temp["Projected_Sales_Value"] / scenario_market * 100,
            np.nan,
        )

        rows.append(temp)

    return pd.concat(rows, ignore_index=True)


def calculate_patient_flow(
    population,
    prevalence_rate,
    diagnosis_rate,
    treatment_rate,
):
    population = float(population)
    prevalence_rate = float(prevalence_rate)
    diagnosis_rate = float(diagnosis_rate)
    treatment_rate = float(treatment_rate)

    disease_population = population * prevalence_rate
    diagnosed_patients = disease_population * diagnosis_rate
    treated_patients = diagnosed_patients * treatment_rate

    return {
        "Population": population,
        "Disease_Population": disease_population,
        "Diagnosed_Patients": diagnosed_patients,
        "Treated_Patients": treated_patients,
    }


def run_patient_flow_scenarios(
    baseline_flow,
    scenarios=None,
):
    scenarios = scenarios or DEFAULT_SCENARIOS
    rows = []

    for name, a in scenarios.items():
        diagnosis_rate = (
            baseline_flow["diagnosis_rate"]
            * (1 + a["diagnosis_rate_change"])
        )
        treatment_rate = (
            baseline_flow["treatment_rate"]
            * (1 + a["treatment_rate_change"])
        )

        result = calculate_patient_flow(
            population=baseline_flow["population"],
            prevalence_rate=baseline_flow["prevalence_rate"],
            diagnosis_rate=diagnosis_rate,
            treatment_rate=treatment_rate,
        )

        result.update({
            "Scenario": name,
            "Diagnosis_Rate_%": diagnosis_rate * 100,
            "Treatment_Rate_%": treatment_rate * 100,
        })
        rows.append(result)

    return pd.DataFrame(rows)


def _minmax_score(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() == 0 or s.max() == s.min():
        return pd.Series(50.0, index=series.index)
    return (s - s.min()) / (s.max() - s.min()) * 100


def add_opportunity_scores(brand_scenarios):
    out = brand_scenarios.copy()

    out["Revenue_Opportunity_Score"] = _minmax_score(
        out["Revenue_Change"]
    )
    out["Market_Share_Score"] = _minmax_score(
        out["Projected_Market_Share_%"]
    )
    out["Scenario_Opportunity_Score"] = (
        out["Revenue_Opportunity_Score"] * 0.70
        + out["Market_Share_Score"] * 0.30
    ).round(2)

    out["Strategic_Action"] = np.select(
        [
            out["Scenario_Opportunity_Score"] >= 80,
            out["Scenario_Opportunity_Score"] >= 60,
            out["Scenario_Opportunity_Score"] >= 40,
            out["Scenario_Opportunity_Score"] >= 20,
        ],
        [
            "Aggressive Investment",
            "Invest & Expand",
            "Defend & Monitor",
            "Selective Investment",
        ],
        default="Deprioritize",
    )

    return out


def downside_risk(brand_scenarios):
    base = brand_scenarios[
        brand_scenarios["Scenario"] == "Base Case"
    ][
        [
            "Brand Name",
            "Manufacturer",
            "Therapeutic Class",
            "Projected_Sales_Value",
        ]
    ].copy()

    downside = brand_scenarios[
        brand_scenarios["Scenario"] == "Downside"
    ][
        [
            "Brand Name",
            "Projected_Sales_Value",
        ]
    ].copy()

    out = base.merge(
        downside,
        on="Brand Name",
        how="left",
        suffixes=("_Base", "_Downside"),
    )

    out["Downside_Revenue_Loss"] = (
        out["Projected_Sales_Value_Base"]
        - out["Projected_Sales_Value_Downside"]
    )

    out["Downside_Loss_%"] = np.where(
        out["Projected_Sales_Value_Base"] > 0,
        out["Downside_Revenue_Loss"]
        / out["Projected_Sales_Value_Base"]
        * 100,
        np.nan,
    )

    return out.sort_values(
        "Downside_Revenue_Loss",
        ascending=False,
    ).reset_index(drop=True)


def scenario_engine(
    project_root=None,
    data_path=None,
    scenarios=None,
    months=12,
    patient_flow=None,
):
    df = load_data(
        project_root=project_root,
        data_path=data_path,
    )

    market = run_market_scenarios(
        df,
        scenarios=scenarios,
        months=months,
    )

    brands = run_brand_scenarios(
        df,
        scenarios=scenarios,
        months=months,
    )

    brands = add_opportunity_scores(brands)
    risks = downside_risk(brands)

    result = {
        "market": market,
        "brands": brands,
        "downside_risk": risks,
    }

    if patient_flow is not None:
        result["patient_flow"] = run_patient_flow_scenarios(
            patient_flow,
            scenarios=scenarios,
        )

    return result
