from vega_cli.tools.builtin.read_file import ReadFileTool
from vega_cli.tools.builtin.list_dir import ListDirTool
from vega_cli.tools.builtin.write_file import WriteFileTool
from vega_cli.tools.builtin.shell import ShellTool


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool):
        self._tools[tool.name] = tool

    def get(self, name):
        return self._tools.get(name)

    def list(self, read_only: bool = False):
        if read_only:
            return [t for t in self._tools.values() if getattr(t, "is_read_only", False)]
        return list(self._tools.values())


registry = ToolRegistry()

registry.register(ReadFileTool())
registry.register(ListDirTool())
registry.register(WriteFileTool())
registry.register(ShellTool())