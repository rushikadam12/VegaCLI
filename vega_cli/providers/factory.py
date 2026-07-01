from vega_cli.providers.base import BaseProvider
from vega_cli.providers.lmstudio import LMStudioProvider


class ProviderFactory:
    """Dispatches to the right provider based on the provider name string."""

    @staticmethod
    def create(provider_name: str) -> BaseProvider:
        if provider_name == "lmstudio":
            return LMStudioProvider()

        raise ValueError(f"Unknown provider: '{provider_name}'. Supported: ['lmstudio']")