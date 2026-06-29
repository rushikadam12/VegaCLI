from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AgentResponse(BaseModel):
    success: bool
    output: str
    steps_count: int
    errors: List[str] = []
