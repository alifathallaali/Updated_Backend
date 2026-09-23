"""
PharmaLens AI — Module 15
Market Access & Institutional Intelligence
Synthetic/demo-ready engines. Replace example data with licensed/authorized data.
"""
from __future__ import annotations
import pandas as pd
import numpy as np

def _num(s, default=0):
    if isinstance(s, (int, float)):
        return pd.Series(default)
    return pd.to_numeric(s, errors="coerce").fillna(default)

def institution_prioritization(df, weights=None):
    x = df.copy()
    weights = weights or {
        "Potential_Value": .30, "Access_Score": .20, "Growth_Score": .15,
        "Competitor_Gap_Score": .15, "Procurement_Score": .10, "Strategic_Score": .10,
    }
    score = pd.Series(0.0, index=x.index)
    for col, weight in weights.items():
        vals = pd.to_numeric(x[col], errors="coerce").fillna(0).clip(0, 100) if col in x else 0
        score += vals * weight
    x["Institution_Opportunity_Score"] = score.round(2)
    x["Priority_Tier"] = pd.cut(
        x["Institution_Opportunity_Score"], [-1, 50, 70, 85, 100],
        labels=["C", "B", "A", "A+"], include_lowest=True
    )
    return x.sort_values("Institution_Opportunity_Score", ascending=False)

def hospital_segmentation(df):
    x = institution_prioritization(df)
    x["Hospital_Segment"] = pd.cut(
        x["Institution_Opportunity_Score"], [-1, 50, 70, 85, 100],
        labels=["Develop", "Growth", "Strategic", "Key Account"], include_lowest=True
    )
    return x

def listing_opportunity_score(df):
    x = df.copy()
    components = {
        "Clinical_Fit_Score": .20, "Hospital_Demand_Score": .20,
        "Formulary_Gap_Score": .15, "Competitor_Gap_Score": .15,
        "Price_Competitiveness_Score": .10, "Patient_Population_Score": .10,
        "Access_Feasibility_Score": .10,
    }
    score = pd.Series(0.0, index=x.index)
    for col, weight in components.items():
        vals = pd.to_numeric(x[col], errors="coerce").fillna(0).clip(0, 100) if col in x else 0
        score += vals * weight
    x["Listing_Opportunity_Score"] = score.round(2)
    return x.sort_values("Listing_Opportunity_Score", ascending=False)

def tender_opportunity_score(df):
    x = df.copy()
    components = {
        "Tender_Timing_Score": .20, "Historical_Demand_Score": .20,
        "Contract_Expiry_Score": .15, "Product_Fit_Score": .15,
        "Competitive_Gap_Score": .10, "Win_Rate_Score": .10,
        "Price_Competitiveness_Score": .10,
    }
    score = pd.Series(0.0, index=x.index)
    for col, weight in components.items():
        vals = pd.to_numeric(x[col], errors="coerce").fillna(0).clip(0, 100) if col in x else 0
        score += vals * weight
    x["Tender_Opportunity_Score"] = score.round(2)
    return x.sort_values("Tender_Opportunity_Score", ascending=False)

def account_share(df, our_sales="Our_Sales", market="Estimated_Account_Market"):
    x = df.copy()
    x[our_sales] = pd.to_numeric(x.get(our_sales, 0), errors="coerce").fillna(0)
    x[market] = pd.to_numeric(x.get(market, 0), errors="coerce").fillna(0)
    x["Account_Share_%"] = np.where(x[market] > 0, x[our_sales] / x[market] * 100, np.nan).round(2)
    x["Untapped_Opportunity_Value"] = (x[market] - x[our_sales]).clip(lower=0)
    return x

def stakeholder_priority(df):
    x = df.copy()
    weights = {"Influence_Score": .35, "Interest_Score": .20, "Access_Score": .20, "Relationship_Score": .25}
    score = pd.Series(0.0, index=x.index)
    for col, weight in weights.items():
        vals = pd.to_numeric(x[col], errors="coerce").fillna(0).clip(0, 100) if col in x else 0
        score += vals * weight
    x["Stakeholder_Priority_Score"] = score.round(2)
    x["Stakeholder_Priority"] = pd.cut(
        x["Stakeholder_Priority_Score"], [-1, 50, 70, 85, 100],
        labels=["Low", "Medium", "High", "Critical"], include_lowest=True
    )
    return x.sort_values("Stakeholder_Priority_Score", ascending=False)

def renewal_probability(df):
    x = df.copy()
    score = pd.Series(50.0, index=x.index)
    factors = {
        "Historical_Renewal_Score": .25, "Supplier_Performance_Score": .15,
        "Price_Competitiveness_Score": .15, "Competitor_Threat_Score": -.15,
        "Stakeholder_Relationship_Score": .15, "Purchase_Trend_Score": .10,
        "Contract_Health_Score": .15,
    }
    for col, weight in factors.items():
        vals = pd.to_numeric(x[col], errors="coerce").fillna(50).clip(0, 100) if col in x else 50
        score += (vals - 50) * weight
    x["Renewal_Probability_%"] = score.clip(0, 100).round(2)
    x["Renewal_Risk"] = pd.cut(
        x["Renewal_Probability_%"], [-1, 40, 60, 80, 100],
        labels=["High Risk", "Watch", "Likely", "Very Likely"], include_lowest=True
    )
    return x

def price_access_tradeoff(price, expected_volume, access_probability_pct):
    return float(price) * float(expected_volume) * float(access_probability_pct) / 100

def classify_access_barrier(formulary_status, procurement_status=None, competitor_contract=False, price_barrier=False):
    if str(formulary_status).lower() in {"non-listed", "not listed", "not_listed"}:
        return "Formulary / Listing Barrier"
    if competitor_contract:
        return "Competitor Contract Barrier"
    if price_barrier:
        return "Price / Access Barrier"
    if procurement_status and str(procurement_status).lower() in {"restricted", "blocked"}:
        return "Procurement Barrier"
    return "No Major Barrier Detected"

def build_account_plan(account):
    return {
        "account_profile": account, "objectives": [], "stakeholders": [],
        "departments": [], "formulary_status": [], "competitors": [],
        "contracts": [], "tenders": [], "opportunities": [], "risks": [],
        "next_actions": [],
    }
