from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class LineSpan:
    start_line: int
    end_line: int
    def ref(self, filename: str) -> str:
        return f"{filename}:L{self.start_line}-L{self.end_line}"

@dataclass(frozen=True)
class TextChunk:
    id: str
    span: LineSpan
    text: str

def chunk_by_lines(lines: List[str], *, max_lines: int = 80, overlap: int = 10) -> List[TextChunk]:
    step = max(1, max_lines - max(0, overlap))
    out: List[TextChunk] = []
    i, n, k = 0, len(lines), 1
    while i < n:
        start, end = i, min(n, i + max_lines)
        span = LineSpan(start+1, end)
        out.append(TextChunk(id=f"chunk_{k:03d}", span=span, text="".join(lines[start:end])))
        k += 1
        i += step
    return out
