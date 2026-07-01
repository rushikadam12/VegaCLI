from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI

from vega_cli.providers.base import BaseProvider
from vega_cli.types.message import Message, ToolCall
from vega_cli.config import settings  # singleton import — no need to pass down


class LMStudioProvider(BaseProvider):
    """
    Provider for LM Studio's OpenAI-compatible local API.
    Reads connection details from the shared settings singleton.
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url=settings.llm_api_base,  # e.g. http://localhost:1234/v1
            api_key=settings.llm_api_key,    # LM Studio accepts any non-empty string
        )
        self._model = settings.llm_model     # e.g. gemma-4-e4b

    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,
    ) -> Message:
        """Call LM Studio and return the assistant Message."""
        # Convert internal Message objects → OpenAI-compatible dicts
        openai_messages = [
            {k: v for k, v in msg.model_dump().items() if v is not None}
            for msg in messages
        ]

        kwargs = dict(model=self._model, messages=openai_messages)
        if tools:
            kwargs["tools"] = tools  # forward tool schemas when provided

        response = await self._client.chat.completions.create(**kwargs)

        choice = response.choices[0].message

        # Map back to our internal Message type
        tool_calls = None
        if choice.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments,
                )
                for tc in choice.tool_calls
            ]

        return Message(
            role="assistant",
            content=choice.content,
            tool_calls=tool_calls,
        )

    async def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[dict]] = None,
    ) -> AsyncIterator[str]:
        """Call LM Studio and yield content chunks as they arrive."""
        openai_messages = [
            {k: v for k, v in msg.model_dump().items() if v is not None}
            for msg in messages
        ]

        kwargs = dict(model=self._model, messages=openai_messages, stream=True)
        if tools:
            kwargs["tools"] = tools

        response_stream = await self._client.chat.completions.create(**kwargs)
        async for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content