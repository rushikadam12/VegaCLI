from typing import Any, Dict, Optional
from pydantic import BaseModel

class Event(BaseModel):
    type: str # 'thought', 'tool_call', 'tool_response', 'error', 'complete'
    data: Dict[str, Any]
