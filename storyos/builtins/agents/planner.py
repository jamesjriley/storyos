from __future__ import annotations
from storyos.config import ProjectConfig
from storyos.core.workspace import Workspace
from storyos.llm.base import LLMMessage

class PlannerAgent:
    def run(self, cfg: ProjectConfig, ws: Workspace, ctx: dict) -> str:
        llm = ctx["llm"]
        target = cfg.project.target_beat_words
        messages = [
            LLMMessage(role="system", content="You are a story beat planner. Output a concise beat plan."),
            LLMMessage(role="user", content=(
                f"Project: {cfg.project.name}\n"
                f"Chapter: {ctx['chapter']}\nBeat: {ctx['beat']}\n\n"
                f"Canon:\n{ctx.get('canon_bundle','')}\n\n"
                f"Chapter outline:\n{ctx.get('chapter_outline','')}\n\n"
                f"Create a beat plan that can be drafted into ~{target} words."
            )),
        ]
        return llm.generate(messages, model=cfg.llm.model, temperature=0.4).text
