from __future__ import annotations
import difflib

class TextTools:
    @staticmethod
    def unified_diff(a: str, b: str, fromfile: str = "before", tofile: str = "after") -> str:
        return "".join(
            difflib.unified_diff(
                a.splitlines(keepends=True),
                b.splitlines(keepends=True),
                fromfile=fromfile,
                tofile=tofile,
            )
        )
