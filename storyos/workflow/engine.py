from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import Dict, Any
from storyos.config import ProjectConfig
from storyos.core.policy import Policy
from storyos.core.runlog import RunLog
from storyos.core.workspace import Workspace
from storyos.llm.openai_adapter_stub import OpenAIAdapterStub
from storyos.plugins.registry import PluginRegistry
from storyos.workflow.steps import (
    load_context_step,
    retrieve_canon_step,
    plan_beat_step,
    draft_beat_step,
    continuity_check_step,
    voice_pass_step,
    user_review_gate_step,
    write_outputs_step,
    write_runlog_step,
)

@dataclass
class RunResult:
    run_id: str
    outputs: Dict[str, Any]

class WorkflowEngine:
    def __init__(self, cfg: ProjectConfig, ws: Workspace):
        self.cfg = cfg
        self.ws = ws
        self.registry = PluginRegistry.builtin()
        self.llm = OpenAIAdapterStub()

    @classmethod
    def from_config(cls, cfg: ProjectConfig, ws: Workspace) -> "WorkflowEngine":
        return cls(cfg, ws)

    def _policy_for(self) -> Policy:
        sec = self.cfg.security
        return Policy(
            allow_cloud_models=sec.allow_cloud_models,
            tool_capabilities=frozenset({"read_file","write_file","search_text"}),
            max_file_read_bytes=sec.max_file_read_kb * 1024,
            max_file_write_bytes=sec.max_file_write_kb * 1024,
        )

    def run(self, chapter: str, beat: str) -> RunResult:
        run_id = uuid.uuid4().hex[:12]
        runlog = RunLog.new(run_id)
        runlog.model = self.cfg.llm.model

        policy = self._policy_for()
        ctx: Dict[str, Any] = {"chapter": chapter, "beat": beat, "policy": policy, "runlog": runlog, "llm": self.llm}

        step_map = {
            "load_context": load_context_step,
            "retrieve_canon": retrieve_canon_step,
            "plan_beat": plan_beat_step,
            "draft_beat": draft_beat_step,
            "continuity_check": continuity_check_step,
            "voice_pass": voice_pass_step,
            "user_review_gate": user_review_gate_step,
            "write_outputs": write_outputs_step,
            "write_runlog": write_runlog_step,
        }

        for step_name in self.cfg.workflow.steps:
            runlog.steps.append(step_name)
            step_map[step_name](cfg=self.cfg, ws=self.ws, registry=self.registry, ctx=ctx)

        runlog.finish()
        return RunResult(run_id=run_id, outputs=runlog.outputs)
