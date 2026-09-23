
"""
PharmaLens AI — Smart Target Planning
Data source adapters and canonical schema.

Design principles:
- IMS/Sales is the company baseline.
- Market Share is calculated from Sales/IMS; no separate MS file is required.
- ATC4 is used as the molecule/therapeutic classification field when a true molecule field is absent.
- Territory percentages are NOT applied to individual product targets.
- RX is time-window aligned before it is used for opportunity.
- Regional product sales are optional; if absent, the engine does not invent them.
"""
from __future__ import annotations
from pathlib import Path
import re
import subprocess
import tempfile
import pandas as pd
import numpy as np

CANONICAL_SALES = {
    "Sector": "Distribution Channel",
    "ATC4": "Therapeutic Class",
    "Corporation": "Manufacturer",
    "Product": "Brand Name",
    "Pack": "Pack Size",
    "Launch Date": "Product Launch",
    "Strength": "Drug Strength",
    "Retail Price": "Selling Price",
    "NFC3": "Market Category",
    "Period": "Month",
    "Calendar Year": "Year",
    "Units": "Sales Units",
    "LC Value": "Sales Value",
}

REQUIRED_SALES = [
    "Brand Name", "Manufacturer", "Therapeutic Class",
    "Sales Units", "Sales Value", "Month", "Year"
]

RX_RENAME = {
    "Molecule": "Molecule",
    "DOC SPEC": "Doctor Specialty",
    "DOC REG": "Region",
    "New Form Code 1": "New Form Code",
    "Product": "Product",
    "MAT Sep 2023\nProj. RX": "MAT RX 2023",
    "MAT Sep 2024\nProj. RX": "MAT RX 2024",
    "MAT Sep 2025\nProj. RX": "MAT RX 2025",
    "RX Growth %": "RX Growth %",
    "MAT Sep 2023 RX": "MAT RX 2023",
    "MAT Sep 2024 RX": "MAT RX 2024",
    "MAT Sep 2025 RX": "MAT RX 2025",
    "2023 RX": "2023 RX",
    "2024 RX": "2024 RX",
    "YTD Sep 2025 RX": "YTD Sep 2025 RX",
}

def _norm(x) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(x).strip().lower()).strip("_")

def read_excel_flexible(path, sheet_name=0, **kwargs):
    path = Path(path)
    if path.suffix.lower() == ".xls":
        try:
            return pd.read_excel(path, sheet_name=sheet_name, **kwargs)
        except ImportError:
            # Production-safe fallback where LibreOffice is available.
            with tempfile.TemporaryDirectory() as td:
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "xlsx",
                     "--outdir", td, str(path)],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                converted = Path(td) / (path.stem + ".xlsx")
                return pd.read_excel(converted, sheet_name=sheet_name, **kwargs)
    return pd.read_excel(path, sheet_name=sheet_name, **kwargs)

def load_sales(path, header=0):
    df = pd.read_excel(path, header=header)
    # Support both original IMS and already-cleaned datasets.
    df = df.rename(columns=CANONICAL_SALES)
    missing = [c for c in REQUIRED_SALES if c not in df.columns]
    if missing:
        raise ValueError(f"IMS/Sales missing required columns: {missing}")
    df = df.copy()
    df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    for c in ["Sales Units", "Sales Value"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    if "Selling Price" in df.columns:
        df["Selling Price"] = pd.to_numeric(df["Selling Price"], errors="coerce")
    return df.dropna(subset=["Month"]).reset_index(drop=True)

def load_processed_parquet(path):
    df = pd.read_parquet(path)
    missing = [c for c in REQUIRED_SALES if c not in df.columns]
    if missing:
        raise ValueError(f"Processed parquet missing required columns: {missing}")
    df = df.copy()
    df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    for c in ["Sales Units", "Sales Value"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df.dropna(subset=["Month"]).reset_index(drop=True)

def load_rx(path, sheet_name="EG MEDICAL NAT"):
    raw = pd.read_excel(path, sheet_name=sheet_name)
    # Keep only non-grand-total rows when present.
    if "Molecule" in raw.columns:
        raw = raw[raw["Molecule"].astype(str).str.strip().str.lower() != "grand total"].copy()
    raw = raw.rename(columns=RX_RENAME)
    for c in [
        "MAT RX 2023", "MAT RX 2024", "MAT RX 2025",
        "RX Growth %", "2023 RX", "2024 RX", "YTD Sep 2025 RX"
    ]:
        if c in raw.columns:
            raw[c] = pd.to_numeric(raw[c], errors="coerce")
    return raw.reset_index(drop=True)

def load_territory_map(path, sheet_name="IMS EST 148 Bricks"):
    raw = read_excel_flexible(path, sheet_name=sheet_name, header=None)
    raw = raw.dropna(how="all").reset_index(drop=True)
    # Expected legacy layout: Clients / Brick Code / Area No. / IMS Brick Code.
    # Preserve raw rows and create best-effort fields.
    cols = list(raw.columns)
    raw.columns = [f"col_{i}" for i in range(len(cols))]
    text = raw.astype(str)
    return raw, text

def load_am_potentiality(path):
    # The workbook has multi-row Arabic headers; keep the raw structure
    # and create a normalized account-level frame.
    xls = pd.ExcelFile(path)
    frames = {}
    for sheet in ["Cairo", "Giza"]:
        if sheet not in xls.sheet_names:
            continue
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        raw = raw.dropna(how="all").reset_index(drop=True)
        frames[sheet] = raw
    return frames

def sales_market_share(df, group_cols=None):
    group_cols = group_cols or ["Brand Name", "Year"]
    work = df.copy()
    denom_cols = [c for c in ["Year", "Month"] if c in group_cols or c == "Year"]
    if "Year" in group_cols:
        denom = work.groupby(["Year"], dropna=False)["Sales Value"].transform("sum")
    else:
        denom = work["Sales Value"].sum()
    work["Market Share"] = np.where(denom > 0, work["Sales Value"] / denom, np.nan)
    return work

def annual_sales(df):
    keys = ["Brand Name", "Manufacturer", "Therapeutic Class", "Year"]
    out = (
        df.groupby(keys, dropna=False, as_index=False)
          .agg(Sales_Units=("Sales Units", "sum"),
               Sales_Value=("Sales Value", "sum"))
          .sort_values(["Brand Name", "Year"])
    )
    out["Unit_Growth"] = out.groupby("Brand Name")["Sales_Units"].pct_change()
    out["Value_Growth"] = out.groupby("Brand Name")["Sales_Value"].pct_change()
    return out
