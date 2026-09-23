"""
PharmaLens AI — FACT / Evidence Data Intelligence Layer
Reusable, schema-tolerant utilities. FACT is real evidence; SYNTHETIC is demo-only.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, re
import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet", ".json"}

ALIASES = {
    "customer_id": ["customer_id","customer key","customer_key","customer code","customer_code","account id","account_id"],
    "customer_name": ["customer_name","customer name","account name","account_name","institution","hospital","customer"],
    "hcp_id": ["hcp_id","hcp key","hcp_key","hcp code","hcp_code","doctor_id","physician_id"],
    "product_id": ["product_id","drug_id","drug code","drug_code","product code","product_code"],
    "product_name": ["product_name","product name","drug","drug_name","brand","brand_name","brand name"],
    "brand_name": ["brand_name","brand name","brand"],
    "molecule": ["molecule","molecule_name","molecule name","generic","generic_name","generic name","active ingredient"],
    "therapeutic_class": ["therapeutic_class","therapeutic class","therapy class","atc","atc_class"],
    "disease": ["disease","disease_name","diagnosis","indication"],
    "region": ["region","region_name","area","territory","territory_name"],
    "channel": ["channel","sales_channel","distribution_channel","distribution channel"],
    "date": ["date","month","period","year_month","transaction_date","rx_date"],
    "year": ["year","yr"],
    "rx": ["rx","prescriptions","prescription","trx","total_rx","rx_count","prescription_count"],
    "units": ["units","sales_units","unit","quantity","qty"],
    "value": ["value","sales_value","sales value","revenue","sales","amount","net_sales"],
    "market_share": ["market_share","market share","share","ms"],
}

@dataclass
class Provenance:
    data_type: str
    source: str
    source_name: str
    source_period: Optional[str]
    retrieval_date: str
    confidence: str
    license_scope: Optional[str] = None

def _norm(x: Any) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)): return ""
    return re.sub(r"\s+", " ", str(x).strip().lower())

def classify_path(path: Path) -> str:
    parts = {_norm(p).replace(" ", "_") for p in path.parts}
    if "fact_raw_data" in parts or "fact" in parts: return "FACT"
    if "synthetic_raw_data" in parts or "synthetic" in parts: return "SYNTHETIC"
    if path.name.lower().startswith("ims"): return "FACT"
    return "UNKNOWN"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def read_table(path: Path, sheet_name: Optional[str]=None) -> pd.DataFrame:
    s=path.suffix.lower()
    if s==".csv":
        for enc in ("utf-8-sig","utf-8","cp1252","latin1"):
            try: return pd.read_csv(path, encoding=enc, low_memory=False)
            except Exception: pass
        raise ValueError(f"Could not decode CSV: {path}")
    if s in {".xlsx",".xls"}: return pd.read_excel(path, sheet_name=sheet_name or 0)
    if s==".parquet": return pd.read_parquet(path)
    if s==".json": return pd.read_json(path)
    raise ValueError(f"Unsupported file: {path}")

def detect_columns(columns: Iterable[str]) -> Dict[str, Optional[str]]:
    normalized={_norm(c):c for c in columns}
    result={}
    for canonical, aliases in ALIASES.items():
        result[canonical]=next((normalized[_norm(a)] for a in aliases if _norm(a) in normalized), None)
    return result

def discover_files(raw_root: Path) -> pd.DataFrame:
    rows=[]
    for p in sorted(raw_root.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            rows.append({"path":str(p),"file_name":p.name,"extension":p.suffix.lower(),
                         "data_type":classify_path(p),"size_mb":round(p.stat().st_size/1048576,3),
                         "sha256":sha256(p)})
    return pd.DataFrame(rows)

def profile_table(df: pd.DataFrame) -> Dict[str, Any]:
    mapping=detect_columns(df.columns)
    date_col=mapping.get("date")
    period=None
    if date_col:
        d=pd.to_datetime(df[date_col], errors="coerce")
        if d.notna().any(): period=f"{d.min().date()} to {d.max().date()}"
    return {"rows":len(df),"columns":len(df.columns),"column_names":[str(c) for c in df.columns],
            "detected_mapping":mapping,"duplicate_rows":int(df.duplicated().sum()),
            "missingness_pct":(df.isna().mean()*100).round(2).to_dict(),
            "source_period_detected":period}

def validate_table(df: pd.DataFrame) -> Dict[str, Any]:
    m=detect_columns(df.columns); errors=[]; warnings=[]
    if df.empty: errors.append("Table is empty.")
    dup=int(df.duplicated().sum())
    if dup: warnings.append(f"{dup} duplicate rows detected.")
    for k in ("rx","units","value"):
        c=m.get(k)
        if c:
            n=pd.to_numeric(df[c],errors="coerce")
            neg=int((n.dropna()<0).sum())
            if neg: warnings.append(f"{k}: {neg} negative values; review source semantics.")
    if m.get("date"):
        invalid=pd.to_datetime(df[m["date"]],errors="coerce").isna().mean()*100
        if invalid: warnings.append(f"date: {invalid:.2f}% invalid/unparsed.")
    return {"status":"FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
            "errors":errors,"warnings":warnings}

def provenance(path: Path, source_name: Optional[str]=None) -> Dict[str,Any]:
    dtype=classify_path(path)
    return asdict(Provenance(
        data_type=dtype,
        source="IQVIA" if "iqvia" in path.name.lower() or path.name.lower().startswith("ims") else "USER_PROVIDED",
        source_name=source_name or path.stem,
        source_period=None,
        retrieval_date=datetime.now(timezone.utc).date().isoformat(),
        confidence="DEMO" if dtype=="SYNTHETIC" else "HIGH",
        license_scope=None))

def guard_real_business_data(data_type: str, allow_synthetic: bool=False) -> None:
    dtype=str(data_type).upper()
    if dtype=="SYNTHETIC" and not allow_synthetic:
        raise ValueError("SYNTHETIC data is restricted to demo/testing/marketing paths.")
    if dtype not in {"FACT","CORPORATE","EXTERNAL","SYNTHETIC"}:
        raise ValueError(f"Explicit data_type required; got {data_type!r}.")
