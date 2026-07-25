import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from vega_cli.agent.agent import Agent
from vega_cli.cli.commands import registry
from vega_cli.cli.renderer import render_info, render_error, render_warning

console = Console()


def _response_panel(content: str, console: Console) -> Panel:
    """Render the final Markdown response panel once after the stream completes."""
    width = max(20, console.width - 4)
    return Panel(
        Markdown(content) if content else Text("(empty response)"),
        title="[bold green]Vega[/bold green]",
        border_style="green",
        padding=(1, 2),
        width=width,
    )


class ChatSession:
    """
    The interactive REPL loop for ASK mode.

    Rendering strategy:
      1. Show a spinner while collecting ALL tokens from the model stream.
         Updating a Live panel during streaming causes terminal ghost artifacts
         when the panel exceeds the visible terminal height (transient=True cannot
         scroll back far enough to erase the panel).
      2. Once the full response is collected, print a SINGLE Markdown panel.
         This gives clean, properly formatted output every time regardless of length.
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

        # Subscribe to agent/tool execution events
        from vega_cli.events.events import event_bus, EVENT_TOOL_CALL, EVENT_TOOL_RESPONSE, EVENT_ERROR
        from vega_cli.cli.renderer import render_event

        event_bus.subscribe(EVENT_TOOL_CALL, render_event)
        event_bus.subscribe(EVENT_TOOL_RESPONSE, render_event)
        event_bus.subscribe(EVENT_ERROR, render_event)

    async def run(self) -> None:
        render_info("Type [green]/help[/green] for commands, [green]/exit[/green] to quit.")
        render_info("ASK Mode started. Chat with Vega below.\n")

        while True:
            try:
                user_input: str = await asyncio.to_thread(
                    lambda: console.input("[bold cyan]You >[/bold cyan] ").strip()
                )
            except (EOFError, KeyboardInterrupt):
                render_info("\nGoodbye!")
                break

            if not user_input:
                continue

            # ── Slash commands ────────────────────────────────────────────────
            is_cmd, should_continue = await registry.execute(user_input, self.agent)
            if is_cmd:
                if not should_continue:
                    break
                cmd_name = user_input.split()[0].lower()
                if cmd_name not in registry.commands:
                    render_warning(f"Unknown command: {user_input}. Type /help for available commands.\n")
                continue

            # ── Collect full response, then render once ───────────────────────
            try:
                response_text = ""

                with console.status("[dim]Thinking…[/dim]", spinner="dots"):
                    async for chunk in self.agent.run_stream(user_input):
                        response_text += chunk

                if not response_text:
                    render_error("No response received from the model.")
                    continue

                console.print(_response_panel(response_text, console))

            except Exception as e:
                render_error(str(e))


# class ChatSession:
#     """
#     The interactive REPL loop for ASK mode.

#     Streaming strategy:
#       1. console.status() spinner while waiting for the FIRST token from the model.
#       2. Once the first token arrives, a Live panel opens and streams plain text into it.
#          Plain text (not Markdown) is used here to avoid Rich re-parsing the full string
#          on every chunk, which causes UI breakage on large responses.
#          - transient=True  → the streaming panel is removed when done (no double box).
#          - auto_refresh=False → redraws only when we call live.refresh() (eliminates flicker).
#          - vertical_overflow='visible' → panel grows down naturally.
#          - Redraws are throttled to every _CHUNK_REDRAW_EVERY chunks for performance.
#       3. Stream ends → Live exits, then the FINAL Markdown-rendered panel is printed once.
#     """

#     def __init__(self, agent: Agent) -> None:
#         self.agent = agent

#         # Subscribe to agent/tool execution events
#         from vega_cli.events.events import event_bus, EVENT_TOOL_CALL, EVENT_TOOL_RESPONSE, EVENT_ERROR
#         from vega_cli.cli.renderer import render_event

#         event_bus.subscribe(EVENT_TOOL_CALL, render_event)
#         event_bus.subscribe(EVENT_TOOL_RESPONSE, render_event)
#         event_bus.subscribe(EVENT_ERROR, render_event)

#     async def run(self) -> None:
#         render_info("Type [green]/help[/green] for commands, [green]/exit[/green] to quit.")
#         render_info("ASK Mode started. Chat with Vega below.\n")

#         while True:
#             try:
#                 user_input: str = await asyncio.to_thread(
#                     lambda: console.input("[bold cyan]You >[/bold cyan] ").strip()
#                 )
#             except (EOFError, KeyboardInterrupt):
#                 render_info("\nGoodbye!")
#                 break

#             if not user_input:
#                 continue

#             # ── Slash commands ────────────────────────────────────────────────
#             is_cmd, should_continue = await registry.execute(user_input, self.agent)
#             if is_cmd:
#                 if not should_continue:
#                     break
#                 cmd_name = user_input.split()[0].lower()
#                 if cmd_name not in registry.commands:
#                     render_warning(f"Unknown command: {user_input}. Type /help for available commands.\n")
#                 continue

#             # ── Stream response ───────────────────────────────────────────────
#             try:
#                 response_text = ""
#                 stream_gen = self.agent.run_stream(user_input)

#                 # Phase 1: spinner while waiting for first token
#                 with console.status("[dim]Thinking…[/dim]", spinner="dots"):
#                     try:
#                         first_chunk = await stream_gen.__anext__()
#                         response_text = first_chunk
#                     except StopAsyncIteration:
#                         first_chunk = None

#                 if first_chunk is None:
#                     render_error("No response received from the model.")
#                     continue

#                 # Phase 2: stream plain text into a Live panel (throttled redraws)
#                 #   transient=True  → removes the streaming panel after done (final panel replaces it)
#                 #   auto_refresh=False → only redraws on explicit live.refresh() calls
#                 #   vertical_overflow='visible' → panel grows down, never truncates
#                 chunk_count = 0
#                 with Live(
#                     _streaming_panel(response_text, console),
#                     refresh_per_second=8,
#                     auto_refresh=False,
#                     transient=True,
#                     vertical_overflow="visible",
#                 ) as live:
#                     async for chunk in stream_gen:
#                         response_text += chunk
#                         chunk_count += 1
#                         if chunk_count % _CHUNK_REDRAW_EVERY == 0:
#                             live.update(_streaming_panel(response_text, console))
#                             live.refresh()

#                 # Phase 3: render full Markdown panel ONCE after stream is complete
#                 console.print(_final_panel(response_text, console))

#             except Exception as e:
#                 render_error(str(e))