from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet

@dataclass(frozen=True)
class Policy:
    allow_cloud_models: bool
    tool_capabilities: FrozenSet[str]
    max_file_read_bytes: int
    max_file_write_bytes: int
