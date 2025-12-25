from __future__ import annotations
from storyos.config import ProjectConfig
from storyos.core.workspace import Workspace
from storyos.llm.base import LLMMessage

class VoiceAgent:
    def run(self, cfg: ProjectConfig, ws: Workspace, ctx: dict) -> str:
        llm = ctx["llm"]
        messages = [
            LLMMessage(role="system", content="You are a line editor focused on voice, rhythm, and specificity."),
            LLMMessage(role="user", content=(
                "Revise the draft for stronger voice and specificity.\n"
                "- Remove generic phrasing and repetition.\n"
                "- Keep facts unchanged.\n"
                "- Keep length roughly similar.\n\n"
                f"Draft:\n{ctx.get('draft_text','')}\n\n"
                f"Continuity notes:\n{ctx.get('continuity_report','')}\n"
            )),
        ]
        return llm.generate(messages, model=cfg.llm.model, temperature=0.5).text
