"""One-call report orchestration from canonical data to local PPTX."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import pandas as pd
from .slide_spec import PresentationSpec, SlideSpec
from .pptx_renderer import render_pptx


def build_presentation_spec(fact_df: pd.DataFrame, *, title: str = "PharmaLens AI Market Review", language: str = "en", max_slides: int = 6) -> PresentationSpec:
    required = {"sales_value", "sales_units", "brand_name", "manufacturer_name", "period_month"}
    missing = required - set(fact_df.columns)
    if missing:
        raise ValueError(f"Canonical dataframe missing: {sorted(missing)}")
    total_value = float(fact_df["sales_value"].sum())
    total_units = float(fact_df["sales_units"].sum())
    top_manufacturers = fact_df.groupby("manufacturer_name", dropna=False)["sales_value"].sum().nlargest(5)
    slides = [
        SlideSpec("Executive Summary", "kpi", metrics=[{"label": "Total Sales Value", "value": round(total_value, 2)}, {"label": "Total Units", "value": round(total_units, 2)}, {"label": "Brands", "value": int(fact_df["brand_name"].nunique())}], evidence=["sales_value.sum", "sales_units.sum", "brand_name.nunique"]),
        SlideSpec("Top Manufacturers", "bar_chart", metrics=[{"label": str(k), "value": float(v)} for k, v in top_manufacturers.items()], evidence=["manufacturer_name", "sales_value.sum by manufacturer"]),
        SlideSpec("Key Observations", "text", bullets=[f"The dataset covers {fact_df['period_month'].min():%b %Y} to {fact_df['period_month'].max():%b %Y}.", f"The top 5 manufacturers contribute {top_manufacturers.sum() / total_value:.1%} of total sales value.", "Use the canonical dataset and validated engine outputs as the source for further decisions."], evidence=["period_month.min/max", "top_manufacturers.sales_value"]),
    ]
    spec = PresentationSpec(title, "Generated from PharmaLens canonical data", slides, language)
    spec.validate(max_slides=max_slides)
    return spec


def generate_ppt_report(fact_df: pd.DataFrame, *, output_path: str | Path = "data/outputs/pharmalens_report.pptx", title: str = "PharmaLens AI Market Review", language: str = "en", max_slides: int = 6, theme: str = "default") -> Path:
    spec = build_presentation_spec(fact_df, title=title, language=language, max_slides=max_slides)
    return render_pptx(spec, output_path, theme=theme)
