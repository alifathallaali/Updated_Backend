
"""
PharmaLens AI — Smart Target Planning API Router

Mount in the existing FastAPI application; do NOT create a second FastAPI app.

Example:
    from smart_target_planning.api_router import router as smart_target_router
    app.include_router(smart_target_router, prefix="/api/v1")
"""
from __future__ import annotations
from typing import Optional, Literal
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .data_sources import load_sales, load_processed_parquet, load_rx
from .target_engine import company_target, build_product_targets, build_region_opportunity, top_down, iterative_reconcile

router = APIRouter(prefix="/targets", tags=["Smart Target Planning"])

class TargetPlanRequest(BaseModel):
    base_year: int = Field(default=2026)
    target_year: int = Field(default=2027)
    objective: Literal["growth","market_share","market_capture","custom"] = "growth"
    method: Literal["top_down","bottom_up","iterative"] = "iterative"
    growth_rate: float = 0.10
    sales_path: Optional[str] = None
    processed_parquet_path: Optional[str] = None
    rx_path: Optional[str] = None

@router.get("/health")
def target_health():
    return {"status":"ok","module":"smart_target_planning","version":"v1"}

@router.post("/validate")
def validate_target_inputs(req: TargetPlanRequest):
    checks = {}
    if req.sales_path:
        try:
            df = load_sales(req.sales_path)
            checks["sales"] = {"ok": True, "rows": len(df), "columns": list(df.columns)}
        except Exception as e:
            checks["sales"] = {"ok": False, "error": str(e)}
    elif req.processed_parquet_path:
        try:
            df = load_processed_parquet(req.processed_parquet_path)
            checks["sales"] = {"ok": True, "rows": len(df), "columns": list(df.columns)}
        except Exception as e:
            checks["sales"] = {"ok": False, "error": str(e)}
    else:
        checks["sales"] = {"ok": False, "error": "sales_path or processed_parquet_path is required"}
    if req.rx_path:
        try:
            rx = load_rx(req.rx_path)
            checks["rx"] = {"ok": True, "rows": len(rx), "columns": list(rx.columns)}
        except Exception as e:
            checks["rx"] = {"ok": False, "error": str(e)}
    return {"valid": all(v["ok"] for v in checks.values()), "checks": checks}

@router.post("/plan")
def create_target_plan(req: TargetPlanRequest):
    try:
        if req.processed_parquet_path:
            sales = load_processed_parquet(req.processed_parquet_path)
        elif req.sales_path:
            sales = load_sales(req.sales_path)
        else:
            raise HTTPException(400, "sales_path or processed_parquet_path is required")

        base = company_target(
            sales, req.base_year, req.target_year,
            objective=req.objective, growth_rate=req.growth_rate
        )
        products = build_product_targets(
            sales, req.base_year, req.target_year, req.growth_rate, req.objective
        )

        result = {
            "company": base,
            "product_targets": products.to_dict(orient="records"),
            "regional_targets": None,
            "method": req.method
        }

        if req.rx_path:
            rx = load_rx(req.rx_path)
            opp = build_region_opportunity(rx)
            regional = top_down(base, opp)
            if req.method == "iterative":
                regional = iterative_reconcile(base, regional)
            result["regional_targets"] = regional.to_dict(orient="records")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/opportunity")
def calculate_opportunity(rx_path: str):
    try:
        rx = load_rx(rx_path)
        opp = build_region_opportunity(rx)
        return {"rows": opp.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(400, str(e))
