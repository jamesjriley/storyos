from __future__ import annotations
from storyos.config import ProjectConfig
from storyos.core.workspace import Workspace
from storyos.llm.base import LLMMessage

class ContinuityAgent:
    def run(self, cfg: ProjectConfig, ws: Workspace, ctx: dict) -> str:
        llm = ctx["llm"]
        messages = [
            LLMMessage(role="system", content="You are a continuity editor. Be picky and list issues clearly."),
            LLMMessage(role="user", content=(
                "Check the draft against canon. List:\n"
                "1) Contradictions\n2) Unclear references\n3) Accidental new entities\n"
                "4) Timeline inconsistencies\n5) Voice drift\n\n"
                f"Canon:\n{ctx.get('canon_bundle','')}\n\n"
                f"Draft:\n{ctx.get('draft_text','')}\n"
            )),
        ]
        return llm.generate(messages, model=cfg.llm.model, temperature=0.2).text
