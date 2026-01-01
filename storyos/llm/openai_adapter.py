from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from storyos.llm.base import LLMAdapter, LLMMessage, LLMResult


@dataclass(frozen=True)
class OpenAIAdapterConfig:
    api_key_env: str = "OPENAI_API_KEY"
    base_url_env: str = "OPENAI_BASE_URL"  # optional
    organization_env: str = "OPENAI_ORG_ID"  # optional


class OpenAIAdapter(LLMAdapter):
    """Real OpenAI adapter using the Responses API via the official Python SDK.

    Auth:
      - Reads API key from env var (default OPENAI_API_KEY)
      - Optional OPENAI_BASE_URL for proxies/gateways
      - Optional OPENAI_ORG_ID if you use org scoping
    """

    def __init__(self, cfg: OpenAIAdapterConfig | None = None):
        self.cfg = cfg or OpenAIAdapterConfig()

        api_key = os.getenv(self.cfg.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key. Set {self.cfg.api_key_env} in your environment.")

        base_url = os.getenv(self.cfg.base_url_env)
        org = os.getenv(self.cfg.organization_env)

        from openai import OpenAI  # type: ignore

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        if org:
            kwargs["organization"] = org

        self.client = OpenAI(**kwargs)

    def generate(
        self,
        messages: List[LLMMessage],
        *,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 2000,
    ) -> LLMResult:
        input_msgs = [
            {"role": m.role, "content": [{"type": "input_text", "text": m.content}]}
            for m in messages
        ]

        if hasattr(self.client, "responses"):
            resp = self.client.responses.create(
                model=model,
                input=input_msgs,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            text = getattr(resp, "output_text", None)
            if not text:
                parts: list[str] = []
                for o in (getattr(resp, "output", None) or []):
                    for c in (getattr(o, "content", None) or []):
                        if getattr(c, "type", None) == "output_text":
                            parts.append(getattr(c, "text", ""))
                text = "\n".join([p for p in parts if p]).strip()
            raw = getattr(resp, "model_dump", lambda: resp)()
        else:
            resp = self.client.chat.completions.create(
                model=model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            text = ""
            if getattr(resp, "choices", None):
                text = (resp.choices[0].message.content or "").strip()
            raw = getattr(resp, "model_dump", lambda: resp)()

        return LLMResult(text=text or "", raw=raw)
