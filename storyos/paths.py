from pathlib import Path
import re
import secrets
from datetime import datetime

# Reserved for path helpers
# --- run id helpers ---------------------------------------------------------

_slug_rx = re.compile(r"[^a-z0-9]+")

def _slugify(s: str, max_len: int = 40) -> str:
    s = (s or "").strip().lower()
    s = _slug_rx.sub("-", s).strip("-")
    if not s:
        return "run"
    return s[:max_len].strip("-") or "run"

def make_run_id(prefix: str = "run", label: str | None = None) -> str:
    ""
 #   Create a human-readable, lexicographically sortable run id.

#    Example: 2025-12-26_00-14-03__ingest__winnie-ch1__a1b2c3
    ""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    p = _slugify(prefix, 24)
    parts = [ts, p]
    if label:
        parts.append(_slugify(label, 40))
    suffix = secrets.token_hex(3)  # 6 hex chars
    return "__".join(parts + [suffix])

# ---------------------------------------------------------------------------
