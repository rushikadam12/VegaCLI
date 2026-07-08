from pathlib import Path
from typing import Dict, Any

from vega_cli.tools.base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to read."
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str) -> str:
        file = Path(path)

        if not file.exists():
            raise FileNotFoundError(f"{path} does not exist.")

        if not file.is_file():
            raise ValueError(f"{path} is not a file.")

        return file.read_text(encoding="utf-8")