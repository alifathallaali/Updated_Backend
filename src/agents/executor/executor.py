from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from src.agents.registry import ToolRegistry
from src.agents.schemas import AgentTask, TaskStatus, WorkerResult
from src.core.contracts import EngineResult

class ParallelExecutor:
    def __init__(self, registry: ToolRegistry, max_workers: int = 8):
        self.registry = registry
        self.max_workers = max_workers

    def _execute_one(self, task: AgentTask) -> WorkerResult:
        task.status = TaskStatus.RUNNING
        try:
            spec = self.registry.resolve(task.tool_name)
            if spec.handler is None:
                raise RuntimeError(f"No handler registered for tool: {task.tool_name}")
            result = spec.handler(task.parameters)
            task.status = TaskStatus.SUCCESS
            return WorkerResult(task.task_id, task.tool_name, result, TaskStatus.SUCCESS)
        except Exception as exc:
            task.status = TaskStatus.ERROR
            return WorkerResult(
                task.task_id,
                task.tool_name,
                EngineResult.failure(task.tool_name, str(exc)).to_dict(),
                TaskStatus.ERROR,
                str(exc),
            )

    def execute(self, tasks: List[AgentTask]) -> List[WorkerResult]:
        independent = [t for t in tasks if t.parallelizable and not t.depends_on]
        sequential = [t for t in tasks if t not in independent]

        indexed = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            future_map = {
                pool.submit(self._execute_one, task): i
                for i, task in enumerate(independent)
            }
            for future in as_completed(future_map):
                indexed.append((future_map[future], future.result()))

        indexed.sort(key=lambda x: x[0])
        results = [r for _, r in indexed]
        results.extend(self._execute_one(t) for t in sequential)
        return results
