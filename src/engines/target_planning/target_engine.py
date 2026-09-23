
"""
PharmaLens AI — Smart Target Planning Engine
Explainable top-down / bottom-up / iterative target planning.

Target hierarchy:
Company -> Region -> Product -> Molecule/Therapeutic Class
Outputs: Units + Value

Important:
- Territory share is a reference for TOTAL Rx/market potential only.
- It is never multiplied directly by a product target.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "market_potential": 0.25,
    "growth": 0.20,
    "share_gap": 0.15,
    "rx_potential": 0.15,
    "molecule_opportunity": 0.10,
    "execution_strength": 0.10,
    "strategic_priority": 0.05,
}

def _minmax(s):
    s = pd.to_numeric(s, errors="coerce").fillna(0)
    if s.max() == s.min():
        return pd.Series(0.5, index=s.index)
    return (s - s.min()) / (s.max() - s.min())

def calculate_company_baseline(sales, base_year=None):
    d = sales.copy()
    d["Year"] = pd.to_numeric(d["Year"], errors="coerce")
    if base_year is None:
        base_year = int(d["Year"].max())
    b = d[d["Year"] == base_year].copy()
    return {
        "base_year": base_year,
        "units": float(b["Sales Units"].sum()),
        "value": float(b["Sales Value"].sum()),
        "rows": int(len(b)),
    }

def company_target(sales, base_year, target_year, objective="growth",
                   growth_rate=0.10, share_capture_rate=None,
                   target_units=None, target_value=None):
    base = calculate_company_baseline(sales, base_year)
    units = base["units"]
    value = base["value"]

    if target_units is not None:
        out_units = float(target_units)
    else:
        out_units = units * (1 + float(growth_rate))

    if target_value is not None:
        out_value = float(target_value)
    else:
        out_value = value * (1 + float(growth_rate))

    return {
        "base_year": base_year, "target_year": target_year,
        "objective": objective,
        "base_units": units, "base_value": value,
        "target_units": out_units, "target_value": out_value,
        "growth_rate": growth_rate,
        "share_capture_rate": share_capture_rate,
    }

def product_baseline(sales, base_year):
    d = sales[sales["Year"] == base_year].copy()
    out = (
        d.groupby(["Brand Name", "Therapeutic Class"], dropna=False, as_index=False)
         .agg(Base_Units=("Sales Units", "sum"),
              Base_Value=("Sales Value", "sum"))
    )
    out["ASP"] = np.where(out["Base_Units"] > 0,
                          out["Base_Value"] / out["Base_Units"], np.nan)
    return out

def build_product_targets(sales, base_year, target_year, growth_rate=0.10,
                          objective="growth", strategic_priority=None):
    p = product_baseline(sales, base_year)
    hist = sales[sales["Year"].between(base_year-2, base_year)].copy()
    if hist.empty:
        hist_growth = pd.DataFrame(columns=["Brand Name", "Hist_Growth"])
    else:
        yearly = hist.groupby(["Brand Name","Year"], as_index=False)["Sales Value"].sum()
        yearly["g"] = yearly.groupby("Brand Name")["Sales Value"].pct_change()
        hist_growth = yearly.groupby("Brand Name", as_index=False)["g"].mean().rename(columns={"g":"Hist_Growth"})
    p = p.merge(hist_growth, on="Brand Name", how="left")
    p["Hist_Growth"] = p["Hist_Growth"].replace([np.inf,-np.inf], np.nan).fillna(growth_rate)
    p["Target_Growth"] = np.clip(
        0.5 * p["Hist_Growth"] + 0.5 * growth_rate,
        -0.10, 0.35
    )
    p["Target_Units"] = p["Base_Units"] * (1 + p["Target_Growth"])
    p["Target_Value"] = p["Base_Value"] * (1 + p["Target_Growth"])
    p["Target_Year"] = target_year
    return p

def build_region_opportunity(region_rx, region_execution=None,
                             weights=None):
    weights = weights or DEFAULT_WEIGHTS
    d = region_rx.copy()

    # Generic expected columns; missing components become neutral.
    components = {}
    for key, col in [
        ("rx_potential", "MAT RX 2025"),
        ("growth", "RX Growth %"),
        ("molecule_opportunity", "MAT RX 2025"),
    ]:
        if col in d.columns:
            components[key] = _minmax(d[col])
        else:
            components[key] = pd.Series(0.5, index=d.index)

    if region_execution is not None:
        ex = region_execution.copy()
        if "Execution Strength" in ex.columns:
            d = d.merge(ex[["Region","Execution Strength"]].drop_duplicates("Region"),
                        on="Region", how="left")
    components["execution_strength"] = _minmax(
        d["Execution Strength"] if "Execution Strength" in d.columns else pd.Series(0.5, index=d.index)
    )
    components["market_potential"] = components["rx_potential"]
    components["share_gap"] = pd.Series(0.5, index=d.index)
    components["strategic_priority"] = pd.Series(0.5, index=d.index)

    score = pd.Series(0.0, index=d.index)
    for k, w in weights.items():
        score = score + float(w) * components[k]
    d["Opportunity_Score"] = score.clip(lower=0)
    return d

def allocate_by_opportunity(total_units, total_value, opportunity_df,
                            key="Region", damping=0.70):
    d = opportunity_df.copy()
    if d.empty:
        return d

    raw = d["Opportunity_Score"].fillna(0.5).astype(float)
    raw = np.maximum(raw, 1e-9)
    weights = raw.pow(damping)
    weights = weights / weights.sum()

    d["Allocation_Weight"] = weights
    d["Target_Units"] = float(total_units) * d["Allocation_Weight"]
    d["Target_Value"] = float(total_value) * d["Allocation_Weight"]
    return d

def top_down(company_target_dict, opportunity_df, damping=0.70):
    return allocate_by_opportunity(
        company_target_dict["target_units"],
        company_target_dict["target_value"],
        opportunity_df,
        damping=damping
    )

def bottom_up(region_targets):
    d = region_targets.copy()
    return {
        "target_units": float(d["Target_Units"].sum()),
        "target_value": float(d["Target_Value"].sum()),
        "regions": d
    }

def iterative_reconcile(company_target_dict, regional_df, max_iter=50,
                         tolerance=1e-6):
    d = regional_df.copy()
    target_u = float(company_target_dict["target_units"])
    target_v = float(company_target_dict["target_value"])
    for _ in range(max_iter):
        su, sv = d["Target_Units"].sum(), d["Target_Value"].sum()
        ru = target_u / su if su else 1.0
        rv = target_v / sv if sv else 1.0
        d["Target_Units"] *= ru
        d["Target_Value"] *= rv
        if abs(d["Target_Units"].sum()-target_u) <= tolerance and \
           abs(d["Target_Value"].sum()-target_v) <= tolerance:
            break
    return d

def explain_target(row):
    reasons = []
    if row.get("Opportunity_Score", 0) >= 0.67:
        reasons.append("high opportunity")
    elif row.get("Opportunity_Score", 0) >= 0.34:
        reasons.append("medium opportunity")
    else:
        reasons.append("lower opportunity")
    if row.get("RX Growth %", 0) > 0.10:
        reasons.append("strong RX growth")
    if row.get("MAT RX 2025", 0) > 0:
        reasons.append("measurable RX potential")
    return "; ".join(reasons)
