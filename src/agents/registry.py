from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from src.core.exceptions import EngineNotFoundError

ToolHandler = Callable[[Dict[str, Any]], Any]

@dataclass
class ToolSpec:
    name: str
    description: str
    engine: str
    handler: Optional[ToolHandler] = None
    deterministic: bool = True
    parallelizable: bool = True
    aliases: List[str] = field(default_factory=list)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec):
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec
        return spec

    def upsert(self, spec: ToolSpec):
        self._tools[spec.name] = spec
        return spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise EngineNotFoundError(f"Tool not registered: {name}") from exc

    def resolve(self, name_or_alias: str) -> ToolSpec:
        if name_or_alias in self._tools:
            return self._tools[name_or_alias]
        needle = name_or_alias.lower().strip()
        for spec in self._tools.values():
            if needle in [a.lower() for a in spec.aliases]:
                return spec
        raise EngineNotFoundError(f"Tool not registered: {name_or_alias}")

    def list(self) -> List[ToolSpec]:
        return list(self._tools.values())

    def names(self) -> List[str]:
        return list(self._tools.keys())

registry = ToolRegistry()
