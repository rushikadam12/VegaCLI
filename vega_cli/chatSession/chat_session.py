import asyncio
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.text import Text

from vega_cli.agent.agent import Agent
from vega_cli.cli.commands import registry
from vega_cli.cli.renderer import render_info, render_error, render_warning

console = Console()


def _response_panel(content: str, console: Console) -> Panel:
    """Build the Vega response panel. Renders Markdown when content exists, spinner otherwise."""
    width = max(20, console.width - 4)
    inner = Markdown(content) if content else Spinner("dots", text="[dim]Thinking…[/dim]")
    return Panel(
        inner,
        title="[bold green]Vega[/bold green]",
        border_style="green",
        padding=(1, 2),
        width=width,
    )


class ChatSession:
    """
    The interactive REPL loop for ASK mode.

    Streaming strategy:
      1. console.status() spinner while waiting for the FIRST token from the model.
      2. Once the first token arrives, a Live panel opens and tokens stream into it as Markdown.
         - transient=False  → the panel stays on screen when the stream ends (no duplicate box).
         - auto_refresh=False → panel only redraws when new data arrives (eliminates background flicker).
         - vertical_overflow='visible' → panel grows down naturally instead of truncating.
      3. Stream ends → Live exits cleanly, final panel is already on screen.
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

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

            # ── Stream response ───────────────────────────────────────────────
            try:
                response_text = ""
                stream_gen = self.agent.run_stream(user_input)

                # Phase 1: spinner while waiting for first token
                with console.status("[dim]Thinking…[/dim]", spinner="dots"):
                    try:
                        first_chunk = await stream_gen.__anext__()
                        response_text = first_chunk
                    except StopAsyncIteration:
                        first_chunk = None

                if first_chunk is None:
                    render_error("No response received from the model.")
                    continue

                # Phase 2: stream into a single Live panel
                #   transient=False  → panel stays on screen after stream ends (no double box)
                #   auto_refresh=False → redraws only on new data (no background flicker)
                #   vertical_overflow='visible' → panel grows down, never truncates
                with Live(
                    _response_panel(response_text, console),
                    refresh_per_second=4,
                    auto_refresh=False,
                    transient=False,
                    vertical_overflow="visible",
                ) as live:
                    async for chunk in stream_gen:
                        response_text += chunk
                        live.update(_response_panel(response_text, console))
                        live.refresh()

            except Exception as e:
                render_error(str(e))