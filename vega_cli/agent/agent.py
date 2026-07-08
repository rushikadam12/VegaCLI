import json
from typing import List, AsyncIterator
from vega_cli.providers.base import BaseProvider
from vega_cli.types.message import Message, ToolCall
from vega_cli.tools.registry import registry
from vega_cli.events.events import (
    event_bus,
    EVENT_TOOL_CALL,
    EVENT_TOOL_RESPONSE,
    EVENT_ERROR,
)


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
        """Add user message, execute ReAct loop with tools, store history, return final answer."""
        self.history.append(Message(role="user", content=user_input))

        from vega_cli.config import settings
        max_loops = settings.max_agent_loops or 10

        loop_count = 0
        while loop_count < max_loops:
            loop_count += 1
            tools = [t.to_openapi_schema() for t in registry.list()]

            response: Message = await self.provider.generate(self.history, tools=tools)

            if response.tool_calls:
                # Store the assistant reply (with tool calls) in history
                self.history.append(response)

                for tool_call in response.tool_calls:
                    tool = registry.get(tool_call.name)
                    if not tool:
                        err_msg = f"Tool '{tool_call.name}' not found in registry."
                        event_bus.publish(EVENT_ERROR, {"message": err_msg})
                        tool_result = err_msg
                    else:
                        try:
                            args = json.loads(tool_call.arguments) if tool_call.arguments else {}
                        except Exception as e:
                            err_msg = f"Failed to parse arguments for tool '{tool_call.name}': {e}"
                            event_bus.publish(EVENT_ERROR, {"message": err_msg})
                            tool_result = err_msg
                            args = None

                        if args is not None:
                            event_bus.publish(
                                EVENT_TOOL_CALL,
                                {"name": tool_call.name, "arguments": args},
                            )
                            try:
                                tool_result = await tool.execute(**args)
                                event_bus.publish(
                                    EVENT_TOOL_RESPONSE,
                                    {"name": tool_call.name, "result": tool_result},
                                )
                            except Exception as e:
                                err_msg = f"Error executing tool '{tool_call.name}': {e}"
                                event_bus.publish(EVENT_ERROR, {"message": err_msg})
                                tool_result = err_msg

                    # Add tool result to context history
                    self.history.append(
                        Message(
                            role="tool",
                            content=str(tool_result),
                            tool_call_id=tool_call.id,
                            name=tool_call.name,
                        )
                    )
                # Query LLM again with tool results
                continue
            else:
                # Store assistant response and return content
                self.history.append(response)
                return response.content or ""

        return "Agent ReAct loop limit reached without a final response."

    async def run_stream(self, user_input: str) -> AsyncIterator[str]:
        """Add user message to history, stream responses, execute tools, and repeat until final answer."""
        self.history.append(Message(role="user", content=user_input))

        from vega_cli.config import settings
        max_loops = settings.max_agent_loops or 10

        loop_count = 0
        while loop_count < max_loops:
            loop_count += 1
            tools = [t.to_openapi_schema() for t in registry.list()]

            tool_calls = []
            full_content = []

            async for chunk in self.provider.generate_stream(
                self.history, tools=tools, tool_calls_out=tool_calls
            ):
                full_content.append(chunk)
                yield chunk

            assistant_reply = "".join(full_content)

            if tool_calls:
                # Store assistant tool call message in history
                assistant_msg = Message(
                    role="assistant",
                    content=assistant_reply if assistant_reply else None,
                    tool_calls=tool_calls,
                )
                self.history.append(assistant_msg)

                for tool_call in tool_calls:
                    tool = registry.get(tool_call.name)
                    if not tool:
                        err_msg = f"Tool '{tool_call.name}' not found in registry."
                        event_bus.publish(EVENT_ERROR, {"message": err_msg})
                        tool_result = err_msg
                    else:
                        try:
                            args = json.loads(tool_call.arguments) if tool_call.arguments else {}
                        except Exception as e:
                            err_msg = f"Failed to parse arguments for tool '{tool_call.name}': {e}"
                            event_bus.publish(EVENT_ERROR, {"message": err_msg})
                            tool_result = err_msg
                            args = None

                        if args is not None:
                            event_bus.publish(
                                EVENT_TOOL_CALL,
                                {"name": tool_call.name, "arguments": args},
                            )
                            try:
                                tool_result = await tool.execute(**args)
                                event_bus.publish(
                                    EVENT_TOOL_RESPONSE,
                                    {"name": tool_call.name, "result": tool_result},
                                )
                            except Exception as e:
                                err_msg = f"Error executing tool '{tool_call.name}': {e}"
                                event_bus.publish(EVENT_ERROR, {"message": err_msg})
                                tool_result = err_msg

                    # Add tool result to context history
                    self.history.append(
                        Message(
                            role="tool",
                            content=str(tool_result),
                            tool_call_id=tool_call.id,
                            name=tool_call.name,
                        )
                    )
                # Loop back to generate response from the model
                continue
            else:
                # No tool calls, store the final assistant reply in history
                assistant_msg = Message(role="assistant", content=assistant_reply)
                self.history.append(assistant_msg)
                break

    def clear_history(self) -> None:
        """Reset conversation history (keeps system prompt if present)."""
        system_msgs = [m for m in self.history if m.role == "system"]
        self.history = system_msgs
