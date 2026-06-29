from os import name
from rich.console import Console
from rich.panel import Panel

console = Console()

def show_header():
    panel = Panel(
        "[bold cyan]VegaCLI[/bold cyan]\n\n"
        "[green]Provider:[/green] LM Studio\n"
        "[green]Model:[/green] Gemma-3n-E4B\n"
        "[green]Version:[/green] 0.1.0",
        title="🚀 AI Agent",
        border_style="cyan",
    )

    console.print(panel)
    console.print("[dim]Type /help for commands[/dim]")
    console.print("[dim]Type /exit to quit[/dim]\n")

def main():
    show_header()
    name = console.input("Enter your name: ")

    console.print(f"[red]Hello {name}[/red]")