import asyncio
from rich.console import Console
from vega_cli.runtime.runtime import RunTime
from vega_cli.cli.renderer import render_interactive_menu, render_info, render_error
from vega_cli.cli.banner import render_banner

console = Console()

def main():
    """
    Main entry point for the CLI. Renders banner, prompts for mode selection,
    and runs the chosen loop.
    """
    # 1. Draw ASCII banner
    render_banner(animate=True,console=console)

    # 2. Setup runtime
    rt = RunTime()
    try:
        # Note: using the runtime's configured 'initalize' method
        rt.initalize()
    except Exception as e:
        render_error(f"Failed to initialize runtime: {e}")
        return

    # TODO:options should be defined here not like this in array
    options = [
        "Ask Mode   (Standard Chat with Memory)",
        "Agent Mode (Coming soon)",
        "Exit"
    ]

    # 3. Mode selection menu loop
    try:
        while True:
            try:
                choice_idx = render_interactive_menu(options, "Select Mode")
            except (EOFError, KeyboardInterrupt):
                console.print()
                render_info("Goodbye!")
                break

            if choice_idx == 0:
                # Start ASK mode
                try:
                    asyncio.run(rt.run())
                except (KeyboardInterrupt, asyncio.CancelledError):
                    console.print()
                    render_info("Exiting Ask Mode...")
                except Exception as e:
                    render_error(f"An unexpected error occurred during chat: {e}")
            elif choice_idx == 1:
                # Stub/placeholder for AGENT mode
                console.print("\n[bold yellow]Agent Mode is not implemented yet.[/bold yellow]")
                render_info("For now, please choose Ask Mode.")
                continue
            elif choice_idx == 2:
                render_info("Goodbye!")
                break
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print()
        render_info("Goodbye!")