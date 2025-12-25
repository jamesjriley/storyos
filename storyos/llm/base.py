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
