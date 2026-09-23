"""Exercise/composite export adapter for the existing PharmaLens report stack."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from src.reports.slide_spec import PresentationSpec, SlideSpec
from src.reports.pptx_renderer import render_pptx


def _text(item: Any) -> str:
    if isinstance(item, str): return item
    if isinstance(item, dict):
        for key in ("text", "finding", "label", "name", "message", "description"):
            if item.get(key): return str(item[key])
        return "; ".join(f"{k}: {v}" for k, v in item.items() if v not in (None, "", [], {}))
    return str(item)


def workspace_to_presentation(workspace: dict[str, Any], *, max_slides: int = 6) -> PresentationSpec:
    """Project governed workspace evidence into the existing PresentationSpec contract."""
    sections = {s["id"]: s for s in workspace.get("sections", []) if s.get("visible")}
    title = f"{workspace.get('id', 'Exercise')} — PharmaLens AI Review"
    status = workspace.get("status", "UNKNOWN")
    quality = workspace.get("quality_status", "UNKNOWN")
    slides = [SlideSpec(
        "Executive Summary", "text",
        bullets=[_text(x) for x in sections.get("summary", {}).get("items", [])] + [f"Status: {status}", f"Quality: {quality}"],
        evidence=[workspace.get("run_id", "")],
    )]
    metrics = sections.get("kpis", {}).get("items", [])
    clean_metrics=[]
    for m in metrics:
        if not isinstance(m, dict): continue
        value=m.get("value", m.get("metric_value"))
        label=m.get("label", m.get("metric", m.get("name", "Metric")))
        if isinstance(value, (int,float)): clean_metrics.append({"label": str(label), "value": value})
    if clean_metrics:
        slides.append(SlideSpec("Key Metrics", "kpi", metrics=clean_metrics[:4], evidence=[workspace.get("run_id", "")]))
    for sid, heading in (("findings","Key Findings"),("opportunities","Opportunities"),("recommendations","Recommendations"),("quality","Quality & Limitations")):
        items=sections.get(sid, {}).get("items", [])
        bullets=[_text(x) for x in items if _text(x)]
        if sid == "quality": bullets += [str(x) for x in workspace.get("limitations", [])]
        if bullets and len(slides) < max_slides:
            slides.append(SlideSpec(heading, "text", bullets=bullets[:8], evidence=[workspace.get("run_id", "")]))
    spec=PresentationSpec(title, "Generated from governed Exercise Workspace evidence", slides[:max_slides], "en")
    spec.validate(max_slides=max_slides)
    return spec


def export_workspace_pptx(workspace: dict[str, Any], output_path: str | Path, *, theme: str = "default", max_slides: int = 6) -> Path:
    return render_pptx(workspace_to_presentation(workspace, max_slides=max_slides), output_path, theme=theme)
