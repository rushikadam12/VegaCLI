# Architectural Decisions

- **gkeepapi for Google Keep**: Google Keep doesn't have an official consumer developer API. We decided to use `gkeepapi` due to its stability, support for master tokens, and active community maintenance.
- **Pydantic for Schemas**: Used Pydantic v2 to validate tool inputs and configurations, ensuring runtime type safety.
- **Rich for Renderer**: Leveraged Rich to display the internal reasoning of the agent (thought steps, tool execution, outputs) clearly and beautifully.
- **OpenAI Client Library for LM Studio**: LM Studio and OpenRouter expose OpenAI-compatible endpoints, allowing us to leverage the standard `openai` Python SDK.
