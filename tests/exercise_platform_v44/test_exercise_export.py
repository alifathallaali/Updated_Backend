from pathlib import Path
from src.exercises.export import workspace_to_presentation, export_workspace_pptx


def _workspace():
    return {
        "id":"STR-004","run_id":"run-1","status":"PARTIAL","quality_status":"WARNING",
        "limitations":["MKT-011 unavailable"],
        "sections":[
            {"id":"summary","visible":True,"items":[{"text":"Evidence-backed strategic review."}]},
            {"id":"kpis","visible":True,"items":[{"label":"Market Share","value":12.5}]},
            {"id":"findings","visible":True,"items":[{"text":"Market share evidence is available."}]},
            {"id":"quality","visible":True,"items":[{"warnings":["partial"]}]},
        ]
    }


def test_workspace_projects_to_existing_presentation_contract():
    spec=workspace_to_presentation(_workspace())
    assert spec.title.startswith("STR-004")
    assert any(s.title == "Key Metrics" for s in spec.slides)
    assert any("MKT-011 unavailable" in b for s in spec.slides for b in s.bullets)


def test_workspace_can_render_real_pptx(tmp_path: Path):
    out=export_workspace_pptx(_workspace(), tmp_path / "str004.pptx")
    assert out.exists()
    assert out.stat().st_size > 1000


def test_report_package_import_is_healthy():
    from src.reports import PresentationSpec, SlideSpec, generate_ppt_report
    assert PresentationSpec and SlideSpec and generate_ppt_report
