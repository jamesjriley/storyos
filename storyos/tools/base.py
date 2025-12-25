from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ToolCall:
    name: str
    args: Dict[str, Any]

class ToolError(Exception):
    pass
