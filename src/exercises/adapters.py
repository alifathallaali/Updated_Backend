from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import importlib
from datetime import datetime, timezone
from uuid import uuid4
import pandas as pd

from .schemas import CanonicalResult, ExerciseRun
from .types import ExerciseStatus, QualityStatus, DataAvailabilityStatus


@dataclass(frozen=True)
class EngineBinding:
    exercise_id: str
    module: str
    callable_name: str
    capability: str
    required_columns: tuple[str, ...] = ()


VERIFIED_BINDINGS: dict[str, EngineBinding] = {
    "MKT-003": EngineBinding("MKT-003", "src.engines.market_intelligence.market_intelligence", "market_share_by_brand", "market_intelligence.market_share_by_brand", ("Brand Name", "Sales Value")),
    "MKT-004": EngineBinding("MKT-004", "src.engines.market_intelligence.market_intelligence", "market_summary", "market_intelligence.market_summary", ("Sales Value", "Sales Units", "Manufacturer", "Brand Name", "Therapeutic Class")),
    "MKT-010": EngineBinding("MKT-010", "src.engines.market_intelligence.market_intelligence", "market_share_by_manufacturer", "market_intelligence.market_share_by_manufacturer", ("Manufacturer", "Sales Value")),
    "TRD-019": EngineBinding("TRD-019", "src.engines.gtm.gtm", "channel_performance", "gtm.channel_performance", ("Distribution Channel", "Sales Value", "Sales Units", "Brand Name")),
    "HCP-015": EngineBinding("HCP-015", "src.engines.medical_affairs.medical_affairs_intelligence", "score_kols", "medical_affairs.score_kols", ("publication_count", "citation_count")),
    "FIN-008": EngineBinding("FIN-008", "src.engines.commercial_finance.commercial_finance", "price_volume_analysis", "commercial_finance.price_volume_analysis", ("Year", "Month", "Selling Price", "Sales Units")),
}


def binding_health(exercise_id: str) -> dict[str, Any]:
    binding = VERIFIED_BINDINGS.get(exercise_id.upper())
    if binding is None:
        return {"exercise_id": exercise_id, "available": False, "reason": "No validated binding registered."}
    try:
        module = importlib.import_module(binding.module)
        callable_obj = getattr(module, binding.callable_name)
    except Exception as exc:
        return {"exercise_id": exercise_id, "available": False, "module": binding.module, "callable": binding.callable_name, "capability": binding.capability, "reason": str(exc)}
    return {"exercise_id": exercise_id, "available": callable(callable_obj), "module": binding.module, "callable": binding.callable_name, "capability": binding.capability}


def _new_run(exercise_id: str, *, data_snapshot=None, user_id=None, organization_id=None, market=None) -> ExerciseRun:
    return ExerciseRun(
        run_id=str(uuid4()), exercise_id=exercise_id, exercise_version="1.0",
        status=ExerciseStatus.CREATED, quality_status=QualityStatus.UNKNOWN,
        created_at=datetime.now(timezone.utc).isoformat(), user_id=user_id,
        organization_id=organization_id, market=market, data_snapshot=data_snapshot,
        engine_versions={}, parameters={},
    )


def _blocked(run: ExerciseRun, message: str) -> ExerciseRun:
    run.status = ExerciseStatus.BLOCKED
    run.quality_status = QualityStatus.BLOCK
    run.error = message
    return run


def _result(run: ExerciseRun, *, summary: str, findings: list[dict[str, Any]], metrics: list[dict[str, Any]], lineage: dict[str, Any], metadata: dict[str, Any]) -> ExerciseRun:
    run.result = CanonicalResult(
        executive_summary=summary,
        key_findings=findings,
        metrics=metrics,
        data_quality={"status": QualityStatus.PASS.value, "availability": DataAvailabilityStatus.COMPLETE.value},
        lineage=lineage,
        metadata=metadata,
    )
    run.status = ExerciseStatus.COMPLETED
    run.quality_status = QualityStatus.PASS
    return run


def run_verified_child(exercise_id: str, df: pd.DataFrame, *, data_snapshot=None, user_id=None, organization_id=None, market=None) -> ExerciseRun:
    """Execute only a validated existing capability; never fabricate a fallback result."""
    exercise_id = exercise_id.upper()
    run = _new_run(exercise_id, data_snapshot=data_snapshot, user_id=user_id, organization_id=organization_id, market=market)
    binding = VERIFIED_BINDINGS.get(exercise_id)
    health = binding_health(exercise_id)
    if binding is None or not health["available"]:
        return _blocked(run, f"Existing engine unavailable for {exercise_id}: {health.get('reason', 'No validated binding.')}")
    missing = [c for c in binding.required_columns if c not in df.columns]
    if missing:
        return _blocked(run, f"Missing required columns: {', '.join(missing)}")

    callable_obj = getattr(importlib.import_module(binding.module), binding.callable_name)
    try:
        if exercise_id == "FIN-008":
            work = df[["Year", "Month", "Selling Price", "Sales Units"]].copy()
            for col in ("Year", "Month", "Selling Price", "Sales Units"):
                work[col] = pd.to_numeric(work[col], errors="coerce")
            work = work.dropna()
            work = work[work["Sales Units"] >= 0]
            if work.empty:
                return _blocked(run, "No valid price/volume rows are available for FIN-008.")
            work["_period"] = work["Year"].astype(int) * 100 + work["Month"].astype(int)
            periods = sorted(work["_period"].unique())
            if len(periods) < 2:
                return _blocked(run, "FIN-008 requires at least two observed periods.")

            def period_inputs(period):
                part = work[work["_period"] == period]
                volume = float(part["Sales Units"].sum())
                if volume > 0:
                    price = float((part["Selling Price"] * part["Sales Units"]).sum() / volume)
                else:
                    price = float(part["Selling Price"].mean())
                return price, volume

            base_price, base_volume = period_inputs(periods[0])
            new_price, new_volume = period_inputs(periods[-1])
            raw = callable_obj(base_price, base_volume, new_price, new_volume)
        else:
            raw = callable_obj(df)
    except Exception as exc:
        return _blocked(run, f"Existing capability failed for {exercise_id}: {exc}")

    lineage = {"engine": binding.module, "capability": binding.capability, "data_snapshot": data_snapshot}
    run.engine_versions = {binding.capability: "existing"}

    if exercise_id == "MKT-003":
        top = raw.head(20)
        share = float(top["Market Share"].sum()) if not top.empty else 0.0
        return _result(run, summary=f"Market share was calculated for {raw['Brand Name'].nunique()} brands using the existing market intelligence engine.",
            findings=[{"id": "MKT-003-TOP-BRANDS", "statement": f"Top {len(top)} brands account for {share:.2f}% of calculated market share.", "evidence_type": "OBSERVED"}],
            metrics=[{"id": "brand_count", "value": int(raw["Brand Name"].nunique()), "unit": "brands", "evidence_type": "OBSERVED"}, {"id": "top_20_share_pct", "value": share, "unit": "%", "evidence_type": "OBSERVED"}], lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id})

    if exercise_id == "MKT-004":
        return _result(run, summary="Observed market summary was calculated using the existing market intelligence engine.",
            findings=[{"id": "MKT-004-SUMMARY", "statement": "The observed market summary is available from the existing capability.", "evidence_type": "OBSERVED"}],
            metrics=[{"id": k, "value": (float(v) if isinstance(v, (int, float)) else v), "evidence_type": "OBSERVED"} for k, v in raw.items()], lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id})

    if exercise_id == "MKT-010":
        top = raw.head(20)
        share = float(top["Market Share"].sum()) if not top.empty else 0.0
        return _result(run, summary=f"Manufacturer share was calculated for {raw['Manufacturer'].nunique()} manufacturers using the existing market intelligence engine.",
            findings=[{"id": "MKT-010-TOP-MANUFACTURERS", "statement": f"Top {len(top)} manufacturers account for {share:.2f}% of calculated market share.", "evidence_type": "OBSERVED"}],
            metrics=[{"id": "manufacturer_count", "value": int(raw["Manufacturer"].nunique()), "unit": "manufacturers", "evidence_type": "OBSERVED"}, {"id": "top_20_share_pct", "value": share, "unit": "%", "evidence_type": "OBSERVED"}], lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id})

    if exercise_id == "TRD-019":
        top = raw.iloc[0] if len(raw) else None
        statement = (f"{top['Distribution Channel']} is the highest observed channel by sales value." if top is not None else "No channel rows were returned.")
        return _result(run, summary="Channel performance was calculated using the existing GTM capability.",
            findings=[{"id": "TRD-019-TOP-CHANNEL", "statement": statement, "evidence_type": "OBSERVED"}],
            metrics=[{"id": "channel_count", "value": int(len(raw)), "unit": "channels", "evidence_type": "OBSERVED"}], lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id})

    if exercise_id == "HCP-015":
        if "kol_influence_score" not in raw.columns:
            return _blocked(run, "Existing KOL capability did not return kol_influence_score.")
        top_score = float(raw["kol_influence_score"].max()) if len(raw) else 0.0
        return _result(run, summary="KOL influence signals were scored using the existing Medical Affairs capability.",
            findings=[{"id": "HCP-015-KOL-SCORING", "statement": f"{len(raw)} KOL candidate rows were scored from available scientific influence inputs.", "evidence_type": "MODELED"}],
            metrics=[{"id": "kol_candidate_count", "value": int(len(raw)), "unit": "candidates", "evidence_type": "OBSERVED"}, {"id": "max_kol_influence_score", "value": top_score, "unit": "score_0_100", "evidence_type": "MODELED"}], lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id})


    if exercise_id == "FIN-008":
        metrics = [
            {"id": key, "value": float(value), "unit": "value", "evidence_type": "MODELED"}
            for key, value in raw.items()
            if key in {"base_revenue", "new_revenue", "price_effect", "volume_effect", "interaction", "total_variance", "variance_pct"}
        ]
        return _result(run, summary="Price-volume decomposition was calculated by the existing Commercial Finance capability using the earliest and latest observed periods.",
            findings=[{"id": "FIN-008-DECOMPOSITION", "statement": "Observed period inputs were decomposed into price, volume and interaction effects.", "evidence_type": "MODELED"}],
            metrics=metrics, lineage=lineage, metadata={"adapter": "existing_engine", "exercise_id": exercise_id, "period_selection": "earliest_vs_latest_observed"})

    return _blocked(run, f"No canonical-result adapter exists for {exercise_id}.")
