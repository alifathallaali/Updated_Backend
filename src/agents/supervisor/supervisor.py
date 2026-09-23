from __future__ import annotations
from typing import Any, Dict, Optional

from src.agents.executor.executor import ParallelExecutor
from src.agents.planner.planner import DeterministicPlanner
from src.agents.registry import ToolRegistry
from src.agents.router.router import AgentRouter
from src.agents.schemas import AgentRun
from src.agents.synthesis.synthesis import DeterministicSynthesizer

class Supervisor:
    def __init__(self, registry: ToolRegistry, planner=None, max_workers=8):
        self.registry = registry
        self.planner = planner or DeterministicPlanner()
        self.router = AgentRouter(registry)
        self.executor = ParallelExecutor(registry, max_workers=max_workers)
        self.synthesizer = DeterministicSynthesizer()

    def run(self, question: str, parameters: Optional[Dict[str, Any]] = None) -> AgentRun:
        plan = self.planner.plan(question, parameters)
        plan.tasks = self.router.route_all(plan.tasks)
        results = self.executor.execute(plan.tasks)
        answer = self.synthesizer.synthesize(question, plan, results)
        return AgentRun(question, plan, results, answer)
