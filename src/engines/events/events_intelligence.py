from __future__ import annotations
import hashlib
import re
import pandas as pd

ALIASES = {
    "event": "activity_name", "event_name": "activity_name", "activity": "activity_name", "name": "activity_name",
    "type": "activity_type", "date": "start_date", "event_date": "start_date", "start": "start_date",
    "end": "end_date", "location": "city", "company": "company_name", "pharma_company": "company_name",
    "manufacturer": "company_name", "organizer_name": "organizer", "therapy_area": "therapeutic_area",
    "ta": "therapeutic_area", "budget": "budget_amount", "budget_value": "budget_amount",
    "currency": "budget_currency", "source": "source_name", "url": "source_url",
}


def _norm(c: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")


def standardize_events(df: pd.DataFrame) -> pd.DataFrame:
    """Pure dataframe version of Project 16 event normalization; no file I/O."""
    out = df.copy()
    out.columns = [_norm(c) for c in out.columns]
    out = out.rename(columns={c: ALIASES[c] for c in out.columns if c in ALIASES})
    defaults = {
        "activity_name": pd.NA, "activity_type": "Unknown", "start_date": pd.NaT, "end_date": pd.NaT,
        "country": "Egypt", "city": pd.NA, "organizer": pd.NA, "company_name": pd.NA,
        "therapeutic_area": "Unknown", "target_audience": pd.NA, "budget_amount": pd.NA,
        "budget_currency": "EGP", "budget_status": "Unknown", "source_name": pd.NA,
        "source_url": pd.NA, "source_last_verified": pd.NaT, "event_status": "Unknown",
    }
    for c, v in defaults.items():
        if c not in out.columns: out[c] = v
    for c in ("start_date", "end_date", "source_last_verified"):
        out[c] = pd.to_datetime(out[c], errors="coerce")
    out["budget_amount"] = pd.to_numeric(out["budget_amount"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    today = pd.Timestamp.now().normalize()
    out["is_future_event"] = out["start_date"] > today
    if "event_id" not in out.columns: out["event_id"] = pd.NA
    def eid(r):
        if pd.notna(r.get("event_id")) and str(r.get("event_id")).strip(): return str(r.get("event_id"))
        base = "|".join(str(r.get(k, "")) for k in ("activity_name", "start_date", "city", "organizer"))
        return "EVT-" + hashlib.sha1(base.encode()).hexdigest()[:12].upper()
    out["event_id"] = out.apply(eid, axis=1)
    return out


def event_portfolio_review(df: pd.DataFrame) -> dict:
    e = standardize_events(df)
    return {"total_events": int(e.event_id.nunique()), "future_events": int(e.is_future_event.sum()),
            "companies": int(e.company_name.nunique(dropna=True)), "therapeutic_areas": int(e.therapeutic_area.nunique(dropna=True)),
            "cities": int(e.city.nunique(dropna=True))}


def event_calendar(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    cols = ["event_id","activity_name","activity_type","start_date","end_date","country","city","organizer","therapeutic_area","event_status","is_future_event"]
    return e[cols].sort_values("start_date", na_position="last").reset_index(drop=True)


def event_budget_review(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    return (e.groupby(["budget_currency","budget_status"], dropna=False)
            .agg(events=("event_id","nunique"), total_budget=("budget_amount","sum"), average_budget=("budget_amount","mean"))
            .reset_index())


def event_geographic_coverage(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    return (e.groupby(["country","city"], dropna=False).agg(total_events=("event_id","nunique"), companies_active=("company_name","nunique"), therapeutic_areas=("therapeutic_area","nunique"), future_events=("is_future_event","sum")).reset_index())


def event_therapeutic_coverage(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    return (e.groupby("therapeutic_area", dropna=False).agg(total_events=("event_id","nunique"), companies_active=("company_name","nunique"), cities=("city","nunique"), future_events=("is_future_event","sum"), total_budget=("budget_amount","sum")).reset_index())


def event_type_mix(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    return e.groupby("activity_type", dropna=False).agg(total_events=("event_id","nunique"), future_events=("is_future_event","sum")).reset_index().sort_values("total_events", ascending=False)


def event_opportunity_calendar(df: pd.DataFrame) -> pd.DataFrame:
    e = standardize_events(df)
    return e[e.is_future_event].sort_values("start_date").reset_index(drop=True)
