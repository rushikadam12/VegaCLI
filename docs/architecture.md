# VegaCLI Architecture

VegaCLI is structured as a modular, event-driven AI agent interface for the terminal.

## Core Modules

1. **Agent (`agent/`)**: Coordinates the reasoning and acting loop (ReAct). Manages model generation requests and state tracking.
2. **Providers (`providers/`)**: Standardizes interfaces to different LLM engines (e.g., LM Studio, OpenRouter).
3. **Tools (`tools/`)**: Modular actions the agent can invoke (e.g., file system actions, shell commands, Google Keep integration).
4. **Context (`context/`)**: Builds prompt templates, collects message histories, and structures system instructions.
5. **History (`history/`)**: Session-based logging of agent executions and conversations.
6. **Events (`events/`)**: An internal event bus allowing components to react to thoughts, actions, and output streams asynchronously.
7. **CLI (`cli/`)**: Command-line parser and terminal UI engine driven by `rich`.
