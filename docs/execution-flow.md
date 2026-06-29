# VegaCLI Execution Flow

The typical flow of execution in VegaCLI is:

1. **Initialization**:
   - CLI command `vega chat` runs `cli/chat.py`.
   - Settings are loaded via `config/loader.py`.
   - The provider client (e.g. `lmstudio.py`) is instantiated.
   - Built-in and custom tools are registered in the `ToolRegistry`.
   - Dependency container stores these singletons.

2. **Conversation Loop**:
   - The user enters a prompt.
   - The prompt is wrapped in standard chat messages via `context/builder.py`.
   - The `AgentLoop` starts.

3. **Reasoning Loop (ReAct)**:
   - The LLM is queried with prompt, user message, system instructions, and tool definitions.
   - The agent yields a **Thought** and decides whether to invoke a **Tool Call**.
   - If a tool is called, the `Runtime` executes the tool with parameters.
   - The output of the tool is fed back into the context.
   - Steps repeat until the agent outputs a final answer or reaches the execution limit.

4. **Event Streaming**:
   - During the loop, events are fired via the `EventBus`.
   - `cli/renderer.py` listens to the event bus to format thoughts, tool runs, and errors in the terminal using Rich.
