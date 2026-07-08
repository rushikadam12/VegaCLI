from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str
    description: str

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Return OpenAI-compatible parameters schema for this tool."""
        pass

    @abstractmethod
    async def execute(self, **kwargs):
        pass

    def to_openapi_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }