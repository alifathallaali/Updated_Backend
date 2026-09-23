from src.agents.registry import ToolRegistry
from src.agents.schemas import AgentTask

class AgentRouter:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def route(self, task: AgentTask) -> AgentTask:
        spec = self.registry.resolve(task.tool_name)
        task.parallelizable = spec.parallelizable
        return task

    def route_all(self, tasks):
        return [self.route(task) for task in tasks]
