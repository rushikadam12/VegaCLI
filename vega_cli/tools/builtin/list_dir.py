from pathlib import Path
from typing import Dict, Any
from vega_cli.tools.base import BaseTool

class ListDirTool(BaseTool):
    name = "list_dir"
    description = "List all files and subdirectories in a directory."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the directory to list (relative or absolute). Defaults to the current working directory."
                }
            }
        }

    async def execute(self, path: str = ".") -> str:
        p = Path(path)
        if not p.exists():
            return f"Directory '{path}' does not exist."
        if not p.is_dir():
            return f"'{path}' is not a directory."
        
        try:
            items = list(p.iterdir())
            if not items:
                return f"Directory '{path}' is empty."
            
            output = []
            for item in sorted(items, key=lambda x: (not x.is_dir(), x.name.lower())):
                prefix = "[DIR] " if item.is_dir() else "[FILE]"
                output.append(f"{prefix} {item.name}")
            return "\n".join(output)
        except Exception as e:
            return f"Error listing directory '{path}': {e}"
