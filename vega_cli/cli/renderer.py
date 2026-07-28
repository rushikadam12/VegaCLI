from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.markdown import Markdown
from vega_cli.types.event import Event


console = Console()



# Interactive menu selection

def render_message(sender: str, text: str, style: str = "green"):
    """
    Renders an agent or assistant message in a styled Panel.
    """
    console.print(
        Panel(
            Markdown(text) if text else Text("(no response)"),
            title=f"[bold {style}]{sender}[/bold {style}]",
            border_style=style,
            padding=(1, 2),
        )
    )

def render_help(commands_help: str):
    """
    Renders the help command details in a Panel.
    """
    console.print(
        Panel(
            commands_help,
            title="[bold cyan]Available Commands[/bold cyan]",
            border_style="cyan"
        )
    )

def render_info(msg: str):
    """
    Renders standard informational message.
    """
    console.print(f"[dim]{msg}[/dim]")

def render_error(msg: str):
    """
    Renders an error message.
    """
    console.print(f"[bold red]Error:[/bold red] {msg}")

def render_warning(msg: str):
    """
    Renders a warning message.
    """
    console.print(f"[bold yellow]Warning:[/bold yellow] {msg}")


# moving cursor
def render_interactive_menu(options: list[str], title: str = "Select Mode") -> int:
    """
    Renders an interactive menu in the terminal using Up/Down arrow keys.
    Returns the index of the selected option.
    """
    import msvcrt
    from rich.live import Live

    selected_index = 0
    
    def make_panel():
        menu_text = Text()
        for idx, opt in enumerate(options):
            if idx == selected_index:
                menu_text.append(f"  ● {opt}\n", style="bold cyan")
            else:
                menu_text.append(f"    {opt}\n", style="dim white")
        
        # Remove trailing newline
        if menu_text.plain.endswith("\n"):
            menu_text.remove_suffix("\n")
            
        current_width = console.width
        panel_width = max(20, current_width - 4)

        return Panel(
            menu_text,
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="cyan",
            padding=(1, 2),
            width=panel_width
        )

    with Live(make_panel(), refresh_per_second=10, auto_refresh=False, transient=True) as live:
        while True:
            live.update(make_panel())
            live.refresh()
            
            try:
                ch = msvcrt.getch()
            except KeyboardInterrupt:
                raise KeyboardInterrupt

            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                if ch2 == b'H':  # Up Arrow
                    selected_index = (selected_index - 1) % len(options)
                elif ch2 == b'P':  # Down Arrow
                    selected_index = (selected_index + 1) % len(options)
            elif ch in (b'\r', b'\n'):  # Enter
                break
            elif ch in (b'\x03', b'\x1a'):  # Ctrl+C or Ctrl+Z
                raise KeyboardInterrupt

    return selected_index


def _detect_lexer(path: str) -> str:
    """Guess a Pygments lexer name from the file extension for syntax highlighting."""
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "jsx": "jsx",
        "tsx": "tsx",
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "toml": "toml",
        "md": "markdown",
        "sh": "bash",
        "bash": "bash",
        "zsh": "bash",
        "ps1": "powershell",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "rs": "rust",
        "go": "go",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "rb": "ruby",
    }.get(ext, "text")

# TODO:reduce tool response lengths and add better prompts for output
def render_event(event: Event):
    """
    Renders agent events (tool calls, tool responses, errors) to the console.
    """
    from rich.syntax import Syntax

    if event.type == "tool_call":
        name = event.data.get("name")
        args = event.data.get("arguments", {})
        args_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
        console.print(f"[bold yellow]🔧 Tool Call:[/bold yellow] [cyan]{name}[/cyan]({args_str})")

    elif event.type == "tool_response":
        name = event.data.get("name")
        result = event.data.get("result", "")
        args = event.data.get("arguments", {})
        result_str = str(result)
        if len(result_str) > 300:
            result_str = result_str[:300] + "\n... (truncated)"
            console.print(f"[bold green]✔ Tool Response ({name}):[/bold green]\n{result_str}\n")
        # For read_file: render with full syntax highlighting
        if name == "read_file":
            path = args.get("path", "")
            lexer = _detect_lexer(path)
            inner = Syntax(
                result_str,
                lexer,
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
            )
        else:
            # For all other tools: render as plain Markdown text
            inner = Markdown(result_str) if result_str else Text("(no output)")

        width = max(20, console.width - 4)
        console.print(
            Panel(
                inner,
                title=f"[bold green]✔ Tool Response ({name})[/bold green]",
                border_style="green",
                padding=(1, 2),
                width=width,
            )
        )

    elif event.type == "error":
        msg = event.data.get("message")
        console.print(f"[bold red]❌ Error:[/bold red] {msg}")

