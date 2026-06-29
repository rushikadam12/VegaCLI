import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # LLM Settings
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "lmstudio"))
    llm_api_base: str = Field(default_factory=lambda: os.getenv("LLM_API_BASE", "http://localhost:1234/v1"))
    llm_api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", "lm-studio"))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "lmstudio-model"))

    # Google Keep settings
    google_keep_email: str = Field(default_factory=lambda: os.getenv("GOOGLE_KEEP_EMAIL", ""))
    google_keep_password: str = Field(default_factory=lambda: os.getenv("GOOGLE_KEEP_PASSWORD", ""))
    google_keep_master_token: str = Field(default_factory=lambda: os.getenv("GOOGLE_KEEP_MASTER_TOKEN", ""))

    # System Settings
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    max_agent_loops: int = Field(default_factory=lambda: int(os.getenv("MAX_AGENT_LOOPS", "10")))
