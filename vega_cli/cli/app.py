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
    #banner
    render_banner(animate=True,console=console)

    #Setup runtime
    rt = RunTime()
    try:
        #  using the runtime's configured 'initalize' method
        rt.initalize()
    except Exception as e:
        render_error(f"Failed to initialize runtime: {e}")
        return

    # TODO:options should be defined here not like this in array
    options = [
        "Ask Mode   (Standard Chat with Memory)",
        "Agent Mode (Autonomous Goal-Directed)",
        "Exit"
    ]

    #Mode selection menu loop
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
                # Start AGENT mode
                try:
                    asyncio.run(rt.run_agent())
                except (KeyboardInterrupt, asyncio.CancelledError):
                    console.print()
                    render_info("Exiting Agent Mode...")
                except Exception as e:
                    render_error(f"An unexpected error occurred during agent execution: {e}")
            elif choice_idx == 2:
                render_info("Goodbye!")
                break
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print()
        render_info("Goodbye!")