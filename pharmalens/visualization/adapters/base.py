"""Base adapter: existing analytics stay authoritative; adapters only present results."""
from typing import Any, Dict, List
from ..chart_spec import ChartSpec

class VisualizationAdapter:
    exercise_key = "base"

    def build(self, result: Dict[str, Any]) -> List[ChartSpec]:
        raise NotImplementedError

    @staticmethod
    def rows(result: Dict[str, Any], key: str) -> list:
        value = result.get(key, [])
        return value if isinstance(value, list) else []

    @staticmethod
    def source(result: Dict[str, Any]) -> str | None:
        return result.get("source") or result.get("provenance", {}).get("source")
