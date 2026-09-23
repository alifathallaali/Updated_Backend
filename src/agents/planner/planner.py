from __future__ import annotations
from typing import Any, Dict, List, Optional
from src.agents.schemas import AgentPlan, AgentTask

class DeterministicPlanner:
    INTENTS = [
        ("market_access", ["market access", "reimbursement", "hta", "payer"]),
        ("tender", ["tender", "bid", "rfq", "procurement"]),
        ("forecast", ["forecast", "future sales", "predict", "prediction"]),
        ("launch", ["launch", "launched", "new product"]),
        ("gtm", ["gtm", "go to market", "distribution", "channel"]),
        ("recommendation", ["recommend", "recommendation", "opportunity", "strategy"]),
        ("similarity", ["similar", "competitor", "competition", "competitors"]),
        ("molecule", ["molecule", "active ingredient", "ingredient"]),
        ("company", ["company", "manufacturer"]),
        ("brand", ["brand", "product performance"]),
        ("market", ["market", "market size", "market growth", "market share"]),
    ]

    TOOL_MAP = {
        "market_access": "market_access_tool",
        "tender": "tender_tool",
        "forecast": "forecast_tool",
        "launch": "launch_tool",
        "gtm": "gtm_tool",
        "recommendation": "recommendation_tool",
        "similarity": "similarity_tool",
        "molecule": "molecule_tool",
        "company": "company_tool",
        "brand": "brand_tool",
        "market": "market_tool",
    }

    def detect_intents(self, question: str) -> List[str]:
        q = question.lower()
        return [
            intent for intent, patterns in self.INTENTS
            if any(pattern in q for pattern in patterns)
        ]

    def plan(self, question: str, parameters: Optional[Dict[str, Any]] = None) -> AgentPlan:
        parameters = dict(parameters or {})
        intents = self.detect_intents(question)
        if not intents:
            return AgentPlan(
                question=question,
                warnings=["No supported analytical intent was detected."]
            )

        tasks = [
            AgentTask(
                task_id=f"task_{i}_{intent}",
                intent=intent,
                tool_name=self.TOOL_MAP[intent],
                parameters=parameters,
            )
            for i, intent in enumerate(intents, 1)
        ]
        return AgentPlan(question=question, tasks=tasks)
