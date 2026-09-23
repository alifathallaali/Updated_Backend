"""Minimal validated presentation contract used by the existing local PPTX renderer."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class SlideSpec:
    title: str
    slide_type: str
    metrics: list[dict[str, Any]] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

@dataclass
class PresentationSpec:
    title: str
    subtitle: str
    slides: list[SlideSpec]
    language: str = "en"

    def validate(self, *, max_slides: int = 6) -> None:
        if not self.title.strip():
            raise ValueError("Presentation title is required")
        if not self.slides:
            raise ValueError("At least one slide is required")
        if len(self.slides) > max_slides:
            raise ValueError(f"Presentation exceeds max_slides={max_slides}")
        for slide in self.slides:
            if not slide.title.strip():
                raise ValueError("Slide title is required")
