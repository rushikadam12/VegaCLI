from abc import ABC, abstractmethod
from typing import List, Optional, AsyncIterator
from vega_cli.types.message import Message


class BaseProvider(ABC):
    """Abstract base class all LLM providers must implement."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,  # OpenAI-format tool schemas
    ) -> Message:
        """Send messages to the LLM and return the assistant reply.

        Args:
            messages: Conversation history including the latest user message.
            tools: Optional list of OpenAI-format tool schemas. When provided,
                   the model may return a Message with tool_calls populated.
        """

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,
    ) -> AsyncIterator[str]:
        """Send messages to the LLM and yield content chunks as they arrive.

        Args:
            messages: Conversation history including the latest user message.
            tools: Optional list of OpenAI-format tool schemas.
        """