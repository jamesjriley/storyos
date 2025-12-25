from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import yaml

@dataclass
class ToolInvocationRecord:
    tool: str
    args: Dict[str, Any]
    ok: bool
    error: str | None = None

@dataclass
class FileAccessRecord:
    path: str
    action: str  # "read"|"write"
    sha256: str | None = None

@dataclass
class RunLog:
    run_id: str
    started_at: str
    finished_at: str | None = None
    model: str | None = None
    steps: List[str] = field(default_factory=list)
    tool_invocations: List[ToolInvocationRecord] = field(default_factory=list)
    file_access: List[FileAccessRecord] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new(run_id: str) -> "RunLog":
        now = datetime.now(timezone.utc).isoformat()
        return RunLog(run_id=run_id, started_at=now)

    def finish(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.__dict__, sort_keys=False, allow_unicode=True)
