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