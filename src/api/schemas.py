from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class AgentAskRequest(BaseModel):
    question: str = Field(min_length=1)
    parameters: Optional[Dict[str, Any]] = None

class AgentAskResponse(BaseModel):
    question: str
    answer: str
    run: Optional[Dict[str, Any]] = None
