"""Central PharmaLens visualization design tokens.

Keep business logic independent from these tokens. Frontend and export renderers
should consume this contract so all exercises share one visual language.
"""
from __future__ import annotations

PHARMALENS_THEME = {
    "name": "pharmalens",
    "font_family": "Inter",
    "radius": 12,
    "background": "var(--pl-background)",
    "surface": "var(--pl-surface)",
    "text": "var(--pl-text)",
    "muted_text": "var(--pl-muted-text)",
    "border": "var(--pl-border)",
    "grid": "var(--pl-grid)",
    "palette": [
        "var(--pl-primary)",
        "var(--pl-secondary)",
        "var(--pl-accent)",
        "var(--pl-positive)",
        "var(--pl-warning)",
        "var(--pl-negative)",
        "var(--pl-neutral)",
    ],
}


def get_theme(name: str = "pharmalens") -> dict:
    if name != "pharmalens":
        raise ValueError(f"Unsupported visualization theme: {name}")
    return PHARMALENS_THEME.copy()
