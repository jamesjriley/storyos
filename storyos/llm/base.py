from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List, Dict, Any

@dataclass
class LLMMessage:
    role: str
    content: str

@dataclass
class LLMResult:
    text: str
    raw: Dict[str, Any]

class LLMClient(Protocol):
    def generate(self, messages: List[LLMMessage], *, model: str, temperature: float) -> LLMResult:
        ...

# --- Added: explicit adapter interface (Protocol) ---
from typing import Protocol, List

class LLMAdapter(Protocol):
    def generate(
        self,
        messages: List["LLMMessage"],
        *,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 2000,
    ) -> "LLMResult":
        ...
