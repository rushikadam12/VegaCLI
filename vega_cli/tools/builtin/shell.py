import asyncio
from typing import Dict, Any
from vega_cli.tools.base import BaseTool

class ShellTool(BaseTool):
    name = "shell"
    description = "Run a terminal/shell command on the user's local machine."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute."
                }
            },
            "required": ["command"]
        }

    async def execute(self, command: str) -> str:
        try:
            # Run the command and capture output
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            stdout_decoded = stdout.decode(errors="replace")
            stderr_decoded = stderr.decode(errors="replace")
            
            output_parts = []
            if stdout_decoded:
                output_parts.append(f"Standard Output:\n{stdout_decoded}")
            if stderr_decoded:
                output_parts.append(f"Standard Error:\n{stderr_decoded}")
            
            if not output_parts:
                output_parts.append("Command executed with no stdout/stderr output.")
            
            return f"Exit Code: {proc.returncode}\n" + "\n".join(output_parts)
        except Exception as e:
            return f"Failed to execute command '{command}': {e}"
