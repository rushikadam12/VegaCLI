from pathlib import Path
from typing import Dict, Any
from vega_cli.tools.base import BaseTool

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write text content to a file at a specific path. Creates directories if they do not exist."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write (relative or absolute)."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file."
                }
            },
            "required": ["path", "content"]
        }

    async def execute(self, path: str, content: str) -> str:
        p = Path(path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Successfully wrote to file '{path}'."
        except Exception as e:
            return f"Error writing file '{path}': {e}"
