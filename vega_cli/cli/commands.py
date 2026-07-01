from typing import Callable, Dict, Awaitable, Tuple
from vega_cli.agent.agent import Agent
from vega_cli.cli.renderer import render_help, render_info

class Command:
    def __init__(self, name: str, description: str, callback: Callable[[Agent], Awaitable[bool]]):
        self.name = name
        self.description = description
        self.callback = callback

class CommandRegistry:
    """
    Registry for slash commands (e.g. /exit, /help, /clear).
    Designed to be extensible and easy to customize/maintain.
    """
    def __init__(self):
        self.commands: Dict[str, Command] = {}

    def register(self, name: str, description: str):
        """
        Decorator to register a command handler.
        """
        def decorator(func: Callable[[Agent], Awaitable[bool]]):
            self.commands[name.lower()] = Command(name, description, func)
            return func
        return decorator

    def get_help_text(self) -> str:
        """
        Generates formatted help text listing all registered commands.
        """
        lines = []
        for cmd in sorted(self.commands.values(), key=lambda c: c.name):
            lines.append(f"  [green]{cmd.name}[/green] — {cmd.description}")
        return "\n".join(lines)

    async def execute(self, user_input: str, agent: Agent) -> Tuple[bool, bool]:
        """
        Executes a command if the user input matches.
        Returns:
            (is_command, should_continue)
        """
        parts = user_input.strip().split()
        if not parts:
            return False, True

        cmd_name = parts[0].lower()
        if not cmd_name.startswith("/"):
            return False, True

        if cmd_name in self.commands:
            should_continue = await self.commands[cmd_name].callback(agent)
            return True, should_continue
        
        return True, True  # A command prefix was used, but it was not recognized
# Global instance of the registry
registry = CommandRegistry()

# ── Register default slash commands ───────────────────────────────────────

@registry.register("/help", "Show all available commands")
async def handle_help(agent: Agent) -> bool:
    help_text = registry.get_help_text()
    render_help(help_text)
    return True

@registry.register("/clear", "Clear the current conversation history")
async def handle_clear(agent: Agent) -> bool:
    agent.clear_history()
    render_info("Conversation history cleared.")
    return True

@registry.register("/exit", "Exit the current session")
async def handle_exit(agent: Agent) -> bool:
    render_info("Exiting session...")
    return False

@registry.register("/quit", "Exit the current session")
async def handle_quit(agent: Agent) -> bool:
    render_info("Exiting session...")
    return False
