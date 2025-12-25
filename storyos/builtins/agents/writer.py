from __future__ import annotations
from storyos.config import ProjectConfig
from storyos.core.workspace import Workspace
from storyos.llm.base import LLMMessage

class WriterAgent:
    def run(self, cfg: ProjectConfig, ws: Workspace, ctx: dict) -> str:
        llm = ctx["llm"]
        target = cfg.project.target_beat_words
        rules = (
            "Rules:\n"
            "- Do NOT introduce new named characters.\n"
            "- Do NOT contradict canon.\n"
            "- If something is unclear, write around it without inventing facts.\n"
            f"- Aim for ~{target} words.\n"
            f"- POV: {cfg.project.default_pov}.\n"
        )
        messages = [
            LLMMessage(role="system", content="You are a careful fiction writer who follows constraints."),
            LLMMessage(role="user", content=(
                f"{rules}\n"
                f"Canon:\n{ctx.get('canon_bundle','')}\n\n"
                f"Beat plan:\n{ctx.get('beat_plan','')}\n\n"
                "Draft the beat now."
            )),
        ]
        return llm.generate(messages, model=cfg.llm.model, temperature=cfg.llm.temperature).text
