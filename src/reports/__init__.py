"""Reporting package. Imports are intentionally side-effect free."""
from .slide_spec import PresentationSpec, SlideSpec
from .report_orchestrator import build_presentation_spec, generate_ppt_report

__all__ = ["PresentationSpec", "SlideSpec", "build_presentation_spec", "generate_ppt_report"]
