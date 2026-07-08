from vega_cli.config import settings
from vega_cli.providers.factory import ProviderFactory
from vega_cli.agent.agent import Agent
from vega_cli.chatSession.chat_session import ChatSession
from vega_cli.prompts.base import Prompt


class RunTime:
    def __init__(self):
        self.config = None
        self.provider = None
        self.agent = None
        self.chat_session = None
        # TODO:add context
        # TODO:add context
        # INOGRE:history for now
        # TODO:add provider
        # TODO:add agent
    def initalize(self):
        self.config = settings

        self.provider = ProviderFactory.create(self.config.llm_provider)

        self.agent = Agent(
            provider=self.provider,
            system_prompt=Prompt.get_system_prompt(),
        )

        self.chat_session = ChatSession(
            agent=self.agent,
            
        )

    async def run(self):
        await self.chat_session.run()

    async def run_agent(self):
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown
        from vega_cli.cli.renderer import render_info, render_error, render_event
        from vega_cli.events.events import event_bus, EVENT_TOOL_CALL, EVENT_TOOL_RESPONSE, EVENT_ERROR
        import asyncio

        console = Console()
        
        # Subscribe to events for this session
        event_bus.subscribe(EVENT_TOOL_CALL, render_event)
        event_bus.subscribe(EVENT_TOOL_RESPONSE, render_event)
        event_bus.subscribe(EVENT_ERROR, render_event)

        render_info("AGENT Mode started. The agent will run autonomously to achieve your goal.\n")

        try:
            goal: str = await asyncio.to_thread(
                lambda: console.input("[bold cyan]Enter Goal >[/bold cyan] ").strip()
            )
        except (EOFError, KeyboardInterrupt):
            render_info("\nGoodbye!")
            return

        if not goal:
            render_error("Goal cannot be empty.")
            return

        render_info(f"Running Agent with Goal: '{goal}'...\n")

        with console.status("[dim]Agent is working…[/dim]", spinner="dots"):
            try:
                final_response = await self.agent.run(goal)
                console.print("\n")
                console.print(
                    Panel(
                        Markdown(final_response) if final_response else "(no final response)",
                        title="[bold green]Agent Final Answer[/bold green]",
                        border_style="green",
                        padding=(1, 2)
                    )
                )
            except Exception as e:
                render_error(f"Agent failed to execute: {e}")