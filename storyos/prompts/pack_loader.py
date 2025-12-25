from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class PackPipeline:
    name: str
    system_prompt: str
    user_prompt: str
    guardrails: List[str]
    schema_text: str
    temperature: float
    max_output_tokens: int


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip() + "\n"


def load_pipeline(*, pack_dir: str, pack: str, pipeline: str) -> PackPipeline:
    pack_root = Path(pack_dir).expanduser().resolve() / pack
    pack_yaml = pack_root / "pack.yaml"
    if not pack_yaml.exists():
        raise FileNotFoundError(f"Pack not found: {pack_yaml}")

    cfg = yaml.safe_load(pack_yaml.read_text(encoding="utf-8"))
    defaults = cfg.get("defaults", {}) or {}
    pipelines = cfg.get("pipelines", {}) or {}
    p = pipelines.get(pipeline)
    if not p:
        raise KeyError(f"Pipeline '{pipeline}' not found in {pack_yaml}")

    system_path = pack_root / p["prompts"]["system"]
    user_path = pack_root / p["prompts"]["user"]
    schema_path = pack_root / p["schema"]

    guardrail_paths = [pack_root / gp for gp in (p.get("guardrails") or [])]
    guardrails = [_read_text(gp) for gp in guardrail_paths]

    return PackPipeline(
        name=f"{pack}:{pipeline}",
        system_prompt=_read_text(system_path),
        user_prompt=_read_text(user_path),
        guardrails=guardrails,
        schema_text=_read_text(schema_path),
        temperature=float(defaults.get("temperature", 0.2)),
        max_output_tokens=int(defaults.get("max_output_tokens", 2500)),
    )
