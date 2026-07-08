from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI

from vega_cli.providers.base import BaseProvider
from vega_cli.types.message import Message, ToolCall
from vega_cli.config import settings  # singleton import — no need to pass down


def _serialize_message(msg: Message) -> dict:
    """Serialize our internal Message to an OpenAI-compatible dictionary."""
    d = {"role": msg.role}
    if msg.content is not None:
        d["content"] = msg.content
    elif msg.role in ("assistant", "tool"):
        d["content"] = None

    if msg.name is not None:
        d["name"] = msg.name

    if msg.tool_call_id is not None:
        d["tool_call_id"] = msg.tool_call_id

    if msg.tool_calls is not None:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": tc.arguments
                }
            }
            for tc in msg.tool_calls
        ]
    return d


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
        openai_messages = [_serialize_message(msg) for msg in messages]

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
        tool_calls_out: Optional[List[ToolCall]] = None,
    ) -> AsyncIterator[str]:
        """Call LM Studio and yield content chunks as they arrive."""
        openai_messages = [_serialize_message(msg) for msg in messages]

        kwargs = dict(model=self._model, messages=openai_messages, stream=True)
        if tools:
            kwargs["tools"] = tools

        response_stream = await self._client.chat.completions.create(**kwargs)
        raw_tool_calls = {}

        async for chunk in response_stream:
            if not chunk.choices or len(chunk.choices) == 0:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                yield delta.content

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in raw_tool_calls:
                        raw_tool_calls[idx] = {"id": None, "name": None, "arguments": []}

                    if tc_delta.id:
                        raw_tool_calls[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            raw_tool_calls[idx]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            raw_tool_calls[idx]["arguments"].append(tc_delta.function.arguments)

        if raw_tool_calls and tool_calls_out is not None:
            for idx in sorted(raw_tool_calls.keys()):
                tc_data = raw_tool_calls[idx]
                # In streaming, id or name might not be present on all chunks, but we check if we gathered them
                if tc_data["name"]:
                    arguments = "".join(tc_data["arguments"])
                    tool_calls_out.append(
                        ToolCall(
                            id=tc_data["id"] or f"call_{idx}",
                            name=tc_data["name"],
                            arguments=arguments,
                        )
                    )