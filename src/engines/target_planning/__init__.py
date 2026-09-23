"""Smart Target Planning engine package.

Keep package import side-effect free. Agent/Copilot orchestration lives outside the
deterministic engine package and must not be required to import target_engine.
"""
from .target_engine import *  # noqa: F401,F403
