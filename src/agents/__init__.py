"""PharmaLens agent package.

Keep package import lightweight: legacy ``agent.py`` currently depends on the
historical ``src.agents.tools`` module, which is not present in this repository
snapshot.  Exercise-aware routing can therefore be imported independently.
"""
from .exercise_copilot import CopilotRoute, resolve_copilot_route, run_copilot_exercise, explain_workspace

__all__ = [
    "CopilotRoute", "resolve_copilot_route", "run_copilot_exercise", "explain_workspace",
    "PharmaLensAgent", "pharmalens_agent",
]


def __getattr__(name):
    if name in {"PharmaLensAgent", "pharmalens_agent"}:
        from .agent import PharmaLensAgent, pharmalens_agent
        return {"PharmaLensAgent": PharmaLensAgent, "pharmalens_agent": pharmalens_agent}[name]
    raise AttributeError(name)
