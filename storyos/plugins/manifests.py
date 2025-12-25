from __future__ import annotations
from pydantic import BaseModel, Field

class PluginManifest(BaseModel):
    id: str
    kind: str  # "agent"|"check"|"exporter"
    version: str = "0.1"
    permissions: list[str] = Field(default_factory=list)
    entrypoint: str  # "package.module:Symbol"
