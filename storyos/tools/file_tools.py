from __future__ import annotations
from storyos.tools.base import ToolError
from storyos.core.workspace import Workspace

class FileTools:
    def __init__(self, ws: Workspace):
        self.ws = ws

    def read_file(self, rel_path: str, max_bytes: int) -> str:
        path = self.ws.safe_path(rel_path)
        data = path.read_bytes()
        if len(data) > max_bytes:
            raise ToolError(f"read_file too large: {rel_path} ({len(data)} bytes)")
        return data.decode("utf-8", errors="replace")

    def write_file(self, rel_path: str, content: str, max_bytes: int) -> None:
        data = content.encode("utf-8")
        if len(data) > max_bytes:
            raise ToolError(f"write_file too large: {rel_path} ({len(data)} bytes)")
        path = self.ws.safe_path(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
