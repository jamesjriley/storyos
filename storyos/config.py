from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.8


class SecurityConfig(BaseModel):
    allow_cloud_models: bool = True
    allowed_workspace_roots: list[str] = Field(default_factory=lambda: ["." ])
    max_file_read_kb: int = 256
    max_file_write_kb: int = 512


class WorkflowConfig(BaseModel):
    steps: list[str] = Field(default_factory=lambda: [
        "load_context",
        "retrieve_canon",
        "plan_beat",
        "draft_beat",
        "continuity_check",
        "voice_pass",
        "user_review_gate",
        "write_outputs",
        "write_runlog",
    ])


class PluginsConfig(BaseModel):
    enabled: dict[str, list[str]] = Field(default_factory=dict)


class ProjectMeta(BaseModel):
    name: str = "Story Project"
    version: str = "0.1"
    default_pov: str = "third_tight"
    target_beat_words: int = 950


class ProjectConfig(BaseModel):
    project: ProjectMeta = Field(default_factory=ProjectMeta)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)


def load_project_config(project_dir: str) -> ProjectConfig:
    path = Path(project_dir) / "project.yaml"
    raw: Dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ProjectConfig.model_validate(raw)
