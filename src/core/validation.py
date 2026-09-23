from __future__ import annotations
from typing import Iterable, Mapping, Any

def require_columns(columns: Iterable[str], required: Iterable[str]) -> None:
    available = set(columns)
    missing = [c for c in required if c not in available]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def validate_mapping(payload: Mapping[str, Any], required: Iterable[str]) -> None:
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
