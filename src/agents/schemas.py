from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"

@dataclass
class AgentTask:
    task_id: str
    intent: str
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    parallelizable: bool = True
    status: TaskStatus = TaskStatus.PENDING

@dataclass
class AgentPlan:
    question: str
    tasks: List[AgentTask] = field(default_factory=list)
    planner_version: str = "v1"
    warnings: List[str] = field(default_factory=list)

@dataclass
class WorkerResult:
    task_id: str
    tool_name: str
    result: Any
    status: TaskStatus = TaskStatus.SUCCESS
    error: Optional[str] = None

@dataclass
class AgentRun:
    question: str
    plan: AgentPlan
    results: List[WorkerResult] = field(default_factory=list)
    final_answer: Optional[str] = None
