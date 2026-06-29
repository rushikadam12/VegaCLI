from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str

class Message(BaseModel):
    role: str # 'system', 'user', 'assistant', 'tool'
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
