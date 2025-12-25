from __future__ import annotations
import re, uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from storyos.config import load_project_config
from storyos.core.workspace import Workspace
from storyos.llm.base import LLMMessage
from storyos.llm.openai_adapter import OpenAIAdapter
from storyos.ingest.chunking import chunk_by_lines
from storyos.ingest.schemas import ExtractorOutput
from storyos.ingest.templates import render_character_md, render_world_md, render_timeline_md
from storyos.prompts.pack_loader import load_pipeline
import json


@dataclass(frozen=True)
class IngestResult:
    run_id: str
    proposals_dir: str

EXTRACTOR_SYSTEM = """You extract structured story information for a human-audited canon.
Return STRICT JSON matching schema:
{"characters":[{"name":"string","facts":[{"claim":"string","confidence":"high|med|low","evidence":[{"source":"file:Lx-Ly","note":""}]}],
"open_questions":[{"question":"string","evidence":[{"source":"file:Lx-Ly","note":""}]}]}],
"world":{"facts":[{"claim":"string","confidence":"high|med|low","evidence":[{"source":"file:Lx-Ly","note":""}]}],
"open_questions":[{"question":"string","evidence":[{"source":"file:Lx-Ly","note":""}]}]},
"timeline":{"events":[{"when":"string","what":"string","confidence":"high|med|low","evidence":[{"source":"file:Lx-Ly","note":""}]}]}}
Rules:
- Evidence MUST refer to provided chunk line ranges.
- Avoid inventing facts; prefer open_questions if unsure.
- Only include names you are confident appear in the text.
"""

def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", s.strip().lower())
    return s.strip("_") or "unnamed"

def extract_to_proposals(*, project_dir: str, input_path: str, max_lines_per_chunk: int=80, overlap: int=10, pack_dir: str='content/packs', pack: str='ingest_v1') -> IngestResult:
    cfg = load_project_config(project_dir)
    ws = Workspace.open(project_dir=project_dir, config=cfg)

    run_id = uuid.uuid4().hex[:12]
    proposals_root = ws.safe_path(f"00_INGEST/proposals/{run_id}")
    proposals_root.mkdir(parents=True, exist_ok=True)

    in_path = Path(input_path).expanduser().resolve()
    raw = in_path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines(keepends=True)
    chunks = chunk_by_lines(lines, max_lines=max_lines_per_chunk, overlap=overlap)

    filename = in_path.name
    chunk_text = "\n\n".join([f"## {c.id} [{c.span.ref(filename)}]\n{c.text}" for c in chunks])

    llm = OpenAIAdapter()
    pipe = load_pipeline(pack_dir=pack_dir, pack=pack, pipeline='ingest_extract')
    system_full = ''.join(pipe.guardrails) + '' + pipe.system_prompt
    user_full = pipe.user_prompt.replace('{{filename}}', filename).replace('{{chunk_text}}', chunk_text)
    messages: List[LLMMessage] = [
        LLMMessage(role='system', content=system_full),
        LLMMessage(role='user', content=user_full),
    ]
    out = llm.generate(messages, model=cfg.llm.model, temperature=pipe.temperature, max_output_tokens=pipe.max_output_tokens).text

    m = re.search(r"\{.*\}\s*$", out, flags=re.DOTALL)
    extracted = ExtractorOutput()
    if m:
        try:
            extracted = ExtractorOutput.model_validate_json(m.group(0))
        except Exception:
            extracted = ExtractorOutput()

    (proposals_root / "00_META.md").write_text(
        f"# Ingest run {run_id}\n\n"
        f"- input: {in_path}\n"
        f"- created_utc: {datetime.now(timezone.utc).isoformat()}\n"
        f"- chunks: {len(chunks)}\n",
        encoding="utf-8",
    )
    (proposals_root / "world.md").write_text(render_world_md(extracted.world), encoding="utf-8")
    (proposals_root / "timeline.md").write_text(render_timeline_md(extracted.timeline), encoding="utf-8")

    chars_dir = proposals_root / "characters"
    chars_dir.mkdir(exist_ok=True)
    for ch in extracted.characters:
        (chars_dir / f"{_slug(ch.name)}.md").write_text(render_character_md(ch), encoding="utf-8")

    # --- Prompt pack audit artefacts + robust JSON parsing (patch v2) ---
    (proposals_root / "raw_llm_output.txt").write_text(out, encoding="utf-8")

    (proposals_root / "prompt.md").write_text(
        "# Prompt (assembled)\n\n"
        "## system\n" + system_full + "\n\n"
        "## user\n" + user_full + "\n",
        encoding="utf-8",
    )
# --- end patch v2 ---

    extracted = ExtractorOutput()
    extracted_dict = {}

    try:
        start = out.find('{')
        end = out.rfind('}')
        if start == -1 or end == -1 or end <= start:
            raise ValueError('No JSON object found in LLM output')
        json_text = out[start:end+1]
        extracted_dict = json.loads(json_text)
        extracted = ExtractorOutput.model_validate(extracted_dict)
    except Exception as e:
        (proposals_root / 'parse_errors.txt').write_text(str(e) + '\n', encoding='utf-8')

    (proposals_root / 'parsed.json').write_text(json.dumps(extracted_dict, indent=2), encoding='utf-8')
    # --- end patch v2 ---
    return IngestResult(run_id=run_id, proposals_dir=str(proposals_root))
