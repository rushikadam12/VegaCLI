from typing import List, AsyncIterator
from vega_cli.providers.base import BaseProvider
from vega_cli.types.message import Message


class Agent:
    """
    Thin orchestration layer between the ChatSession and the provider.
    Maintains conversation history so the LLM has memory across turns.
    """

    def __init__(self, provider: BaseProvider, system_prompt: str = "") -> None:
        self.provider = provider
        self.history: List[Message] = []

        # Seed history with system prompt if provided
        if system_prompt:
            self.history.append(Message(role="system", content=system_prompt))

    async def run(self, user_input: str) -> str:
        """Add user message, call provider with full history, store reply, return text."""
        self.history.append(Message(role="user", content=user_input))

        response: Message = await self.provider.generate(self.history)

        # Store assistant reply in history for next turn
        self.history.append(response)

        return response.content or ""

    async def run_stream(self, user_input: str) -> AsyncIterator[str]:
        """Add user message to history, yield response tokens, and save full response to history."""
        self.history.append(Message(role="user", content=user_input))

        full_content = []
        async for chunk in self.provider.generate_stream(self.history):
            full_content.append(chunk)
            yield chunk

        # Store complete response in history
        assistant_reply = "".join(full_content)
        self.history.append(Message(role="assistant", content=assistant_reply))

    def clear_history(self) -> None:
        """Reset conversation history (keeps system prompt if present)."""
        system_msgs = [m for m in self.history if m.role == "system"]
        self.history = system_msgs
