from __future__ import annotations
from typing import List
from storyos.llm.base import LLMClient, LLMMessage, LLMResult

class OpenAIAdapterStub(LLMClient):
    def generate(self, messages: List[LLMMessage], *, model: str, temperature: float) -> LLMResult:
        joined = "\n\n".join([f"[{m.role}] {m.content}" for m in messages])
        fake = f"(STUB LLM OUTPUT)\nModel={model} temp={temperature}\n\n{joined}\n"
        return LLMResult(text=fake, raw={"stub": True})
