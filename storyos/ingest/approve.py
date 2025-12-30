from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# --- confidence normalisation ---
CONF_MAP = {
    "high": "high",
    "med": "med",
    "medium": "med",
    "low": "low",
}


def _normalise_confidence(obj: Any) -> Any:
    """Walk nested dict/list and normalise confidence fields to high|med|low."""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if k == "confidence" and isinstance(v, str):
                out[k] = CONF_MAP.get(v.strip().lower(), v)
            else:
                out[k] = _normalise_confidence(v)
        return out
    if isinstance(obj, list):
        return [_normalise_confidence(x) for x in obj]
    return obj


def safe_slug(text: str) -> str:
    """Filesystem-friendly slug for filenames/paths."""
    s = (text or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "item"


@dataclass
class ApprovalResult:
    run_id: str
    approved_dir: Path
    world_facts_added: int
    timeline_events_added: int
    characters_touched: int
    character_facts_added: int


def _extract_first_json_object(text: str) -> str:
    """Return the first top-level JSON object substring from text.

    We intentionally look for a single {...} object (not double braces).
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    return text[start : end + 1]


def _load_extractor_json(raw_llm_output: Path) -> Dict[str, Any]:
    raw = raw_llm_output.read_text(encoding="utf-8", errors="replace")
    json_text = _extract_first_json_object(raw)
    data = json.loads(json_text)
    if not isinstance(data, dict):
        raise ValueError("Extractor JSON root must be an object")
    return _normalise_confidence(data)


def _ensure_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _append_section(md_path: Path, title: str, lines: List[str]) -> None:
    existing = ""
    if md_path.exists():
        existing = md_path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n"
    block = [""]
    block.append(f"## {title}")
    block.extend(lines)
    md_path.write_text(existing + "\n".join(block).rstrip() + "\n", encoding="utf-8")


def _format_fact_lines(facts: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for f in facts:
        claim = (f.get("claim") or "").strip()
        if not claim:
            continue
        conf = (f.get("confidence") or "").strip()
        tag = f" ({conf})" if conf else ""
        out.append(f"- {claim}{tag}")
        ev = _ensure_list(f.get("evidence"))
        for e in ev:
            if not isinstance(e, dict):
                continue
            src = (e.get("source") or "").strip()
            note = (e.get("note") or "").strip()
            if src or note:
                # keep evidence short; this is canon-facing provenance
                bit = f"    - evidence: {src}" if src else "    - evidence:"
                if note:
                    bit += f" — {note}"
                out.append(bit)
    return out


def approve_proposals(
    *,
    project_dir: str | Path,
    run_id: str,
    dry_run: bool = False,
) -> ApprovalResult:
    """Approve an ingest proposal run into canon.

    Expected layout (created by `storyos ingest extract`):
      <project_dir>/00_INGEST/proposals/<run_id>/raw_llm_output.txt

    Writes/updates:
      <project_dir>/01_CANON/world.md
      <project_dir>/01_CANON/timeline.md
      <project_dir>/02_CHARACTERS/<slug>.md
      <project_dir>/00_INGEST/approved/<run_id>/APPROVAL_REPORT.md

    This is deliberately conservative: it appends new sections tagged with run_id,
    leaving existing canon intact and auditable.
    """

    project_root = Path(project_dir)
    proposals_root = project_root / "00_INGEST" / "proposals" / run_id
    raw_llm_output = proposals_root / "raw_llm_output.txt"
    if not raw_llm_output.exists():
        raise FileNotFoundError(f"Missing raw LLM output at: {raw_llm_output}")

    data = _load_extractor_json(raw_llm_output)

    canon_world = project_root / "01_CANON" / "world.md"
    canon_timeline = project_root / "01_CANON" / "timeline.md"
    canon_chars_dir = project_root / "02_CHARACTERS"

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # World
    world_obj = data.get("world") or {}
    world_facts = _ensure_list(world_obj.get("facts"))
    world_lines = _format_fact_lines([x for x in world_facts if isinstance(x, dict)])

    # Timeline
    tl_obj = data.get("timeline") or {}
    events = _ensure_list(tl_obj.get("events"))
    tl_lines: List[str] = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        when = (ev.get("when") or "").strip()
        what = (ev.get("what") or "").strip()
        if not what:
            continue
        conf = (ev.get("confidence") or "").strip()
        tag = f" ({conf})" if conf else ""
        prefix = f"- {when}: {what}{tag}" if when else f"- {what}{tag}"
        tl_lines.append(prefix)
        for e in _ensure_list(ev.get("evidence")):
            if not isinstance(e, dict):
                continue
            src = (e.get("source") or "").strip()
            note = (e.get("note") or "").strip()
            if src or note:
                bit = f"    - evidence: {src}" if src else "    - evidence:"
                if note:
                    bit += f" — {note}"
                tl_lines.append(bit)

    # Characters
    characters = _ensure_list(data.get("characters"))
    chars_touched = 0
    char_facts_added = 0

    report_lines: List[str] = [
        f"# Approval report",
        f"",
        f"- run_id: `{run_id}`",
        f"- approved_at: {stamp}",
        f"- dry_run: {dry_run}",
        "",
        "## Summary",
    ]

    if world_lines:
        report_lines.append(f"- World facts appended: {len([l for l in world_lines if l.startswith('- ')])}")
    else:
        report_lines.append("- World facts appended: 0")

    if tl_lines:
        report_lines.append(f"- Timeline events appended: {len([l for l in tl_lines if l.startswith('- ')])}")
    else:
        report_lines.append("- Timeline events appended: 0")

    report_lines.append("- Characters updated: TBD")
    report_lines.append("")

    if not dry_run:
        canon_chars_dir.mkdir(parents=True, exist_ok=True)

    # Write world/timeline
    if world_lines and not dry_run:
        _append_section(
            canon_world,
            title=f"Approved ingest facts ({run_id})",
            lines=[f"_approved: {stamp}_", ""] + world_lines,
        )

    if tl_lines and not dry_run:
        _append_section(
            canon_timeline,
            title=f"Approved ingest events ({run_id})",
            lines=[f"_approved: {stamp}_", ""] + tl_lines,
        )

    # Characters write
    for ch in characters:
        if not isinstance(ch, dict):
            continue
        name = (ch.get("name") or "").strip()
        if not name:
            continue
        facts = [x for x in _ensure_list(ch.get("facts")) if isinstance(x, dict)]
        lines = _format_fact_lines(facts)
        if not lines:
            continue

        chars_touched += 1
        char_facts_added += len([l for l in lines if l.startswith("- ")])

        md_name = safe_slug(name) + ".md"
        md_path = canon_chars_dir / md_name

        if not dry_run:
            if not md_path.exists():
                md_path.write_text(f"# {name}\n\n", encoding="utf-8")
            _append_section(
                md_path,
                title=f"Approved ingest facts ({run_id})",
                lines=[f"_approved: {stamp}_", ""] + lines,
            )

    # Approval archive
    approved_dir = project_root / "00_INGEST" / "approved" / run_id
    if not dry_run:
        approved_dir.mkdir(parents=True, exist_ok=True)
        (approved_dir / "source_proposals_path.txt").write_text(
            str(proposals_root), encoding="utf-8"
        )

    report_lines = [
        *report_lines[:],
        "## Characters",
        f"- Characters updated: {chars_touched}",
        f"- Character facts appended: {char_facts_added}",
        "",
        "## Notes",
        "- Canon is appended-only; you can manually refactor/merge later.",
        "- Each section is tagged with run_id for provenance.",
        "- If you re-run approvals, you may create duplicates; treat this command as one-shot per run.",
        "",
    ]

    if not dry_run:
        (approved_dir / "APPROVAL_REPORT.md").write_text(
            "\n".join(report_lines).rstrip() + "\n", encoding="utf-8"
        )

    return ApprovalResult(
        run_id=run_id,
        approved_dir=approved_dir,
        world_facts_added=len([l for l in world_lines if l.startswith("- ")]),
        timeline_events_added=len([l for l in tl_lines if l.startswith("- ")]),
        characters_touched=chars_touched,
        character_facts_added=char_facts_added,
    )

def _format_fact_line(claim: str, confidence: str | None = None) -> str:
    conf = (confidence or "").strip().lower()
    conf = CONF_MAP.get(conf, conf) if conf else ""
    suffix = f" ({conf})" if conf else ""
    return f"- {claim}{suffix}".rstrip()


def _format_event_line(when: str, what: str, confidence: str | None = None) -> str:
    when = (when or "").strip()
    what = (what or "").strip()
    base = f"- {when}: {what}" if when else f"- {what}"
    conf = (confidence or "").strip().lower()
    conf = CONF_MAP.get(conf, conf) if conf else ""
    return f"{base} ({conf})" if conf else base


def _append_section(md_path: Path, title: str, lines: List[str]) -> None:
    if not lines:
        return
    existing = ""
    if md_path.exists():
        existing = md_path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n\n"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    block = [f"## {title}", f"_Approved: {stamp}_", ""] + lines + [""]
    md_path.write_text(existing + "\n".join(block), encoding="utf-8")


def _read_existing_claims(md_path: Path) -> set[str]:
    """Very simple dedupe: extract bullet text after '- ' up to optional ' (conf)' suffix."""
    if not md_path.exists():
        return set()
    text = md_path.read_text(encoding="utf-8", errors="replace")
    claims: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        s = line.lstrip("-").strip()
        # strip trailing confidence marker '(high|med|low|medium)'
        s = re.sub(r"\s*\((high|med|low|medium)\)\s*$", "", s, flags=re.I).strip()
        if s:
            claims.add(s)
    return claims


def approve_proposals_run(
    project_dir: str,
    run_id: str,
    dry_run: bool = False,
    archive: bool = True,
    dedupe: bool = True,
) -> ApprovalResult:
    dedupe = True
    """Approve an ingest proposals run and merge into canon.

    Inputs
    - project_dir: path to a StoryOS project
    - run_id: folder name under 00_INGEST/proposals/<run_id>

    What it does
    - Parses 00_INGEST/proposals/<run_id>/raw_llm_output.txt for the extractor JSON.
    - Appends approved facts/events into:
        - 01_CANON/world.md
        - 01_CANON/timeline.md
        - 02_CHARACTERS/<character>.md (creates if missing)
    - Writes an approval report under 00_INGEST/approved/<run_id>/.

    Notes
    - This is intentionally conservative: it appends, it doesn't rewrite.
    - If you want richer merging (sections, structured tables, conflict resolution),
      keep this as the stable base and add a smarter merger later.
    """

    project_dir = Path(project_dir)
    proposals_root = project_dir / "00_INGEST" / "proposals" / run_id
    if not proposals_root.exists():
        raise FileNotFoundError(f"No proposals run found: {proposals_root}")

    raw_llm_output = proposals_root / "raw_llm_output.txt"
    if not raw_llm_output.exists():
        raise FileNotFoundError(f"Missing raw_llm_output.txt in: {proposals_root}")

    data = _load_extractor_json(raw_llm_output)

    canon_world = project_dir / "01_CANON" / "world.md"
    canon_timeline = project_dir / "01_CANON" / "timeline.md"
    canon_chars_dir = project_dir / "02_CHARACTERS"
    canon_chars_dir.mkdir(parents=True, exist_ok=True)

    approved_dir = project_dir / "00_INGEST" / "approved" / run_id

    # --- gather world facts ---
    world_obj = (data.get("world") or {})
    world_facts = _ensure_list(world_obj.get("facts"))

    world_lines: List[str] = []
    existing_world = _read_existing_claims(canon_world) if dedupe else set()
    for f in world_facts:
        if not isinstance(f, dict):
            continue
        claim = (f.get("claim") or "").strip()
        if not claim:
            continue
        if dedupe and claim in existing_world:
            continue
        world_lines.append(_format_fact_line(claim, f.get("confidence")))

    # --- gather timeline events ---
    tl_obj = (data.get("timeline") or {})
    events = _ensure_list(tl_obj.get("events"))

    tl_lines: List[str] = []
    existing_tl = _read_existing_claims(canon_timeline) if dedupe else set()
    for ev in events:
        if not isinstance(ev, dict):
            continue
        when = (ev.get("when") or "").strip()
        what = (ev.get("what") or "").strip()
        if not what:
            continue
        # dedupe uses the full rendered line without confidence
        dedupe_key = f"{when}: {what}" if when else what
        if dedupe and dedupe_key in existing_tl:
            continue
        tl_lines.append(_format_event_line(when, what, ev.get("confidence")))

    # --- gather character facts ---
    characters = _ensure_list(data.get("characters"))
    chars_touched = 0
    char_facts_added = 0
    char_blocks: List[Tuple[str, List[str]]] = []

    for c in characters:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or "").strip()
        if not name:
            continue
        facts = _ensure_list(c.get("facts"))
        if not facts:
            continue

        md_path = canon_chars_dir / f"{safe_slug(name)}.md"
        existing = _read_existing_claims(md_path) if dedupe else set()

        lines: List[str] = []
        for f in facts:
            if not isinstance(f, dict):
                continue
            claim = (f.get("claim") or "").strip()
            if not claim:
                continue
            if dedupe and claim in existing:
                continue
            lines.append(_format_fact_line(claim, f.get("confidence")))

        if lines:
            chars_touched += 1
            char_facts_added += len(lines)
            char_blocks.append((name, lines))

    # --- apply writes ---
    if not dry_run:
        approved_dir.mkdir(parents=True, exist_ok=True)

        if world_lines:
            _append_section(canon_world, f"Approved ingest facts ({run_id})", world_lines)

        if tl_lines:
            _append_section(canon_timeline, f"Approved ingest timeline ({run_id})", tl_lines)

        for name, lines in char_blocks:
            md_path = canon_chars_dir / f"{safe_slug(name)}.md"
            if not md_path.exists():
                # create a minimal scaffold
                md_path.write_text(f"# {name}\n\n", encoding="utf-8")
            _append_section(md_path, f"Approved ingest facts ({run_id})", lines)

        # Write a report so humans can audit what got merged.
        report_lines: List[str] = [
            f"# Approval report: {run_id}",
            "",
            f"Project: {project_dir.resolve()}",
            "",
            "## Summary",
            f"- World facts added: {len(world_lines)}",
            f"- Timeline events added: {len(tl_lines)}",
            f"- Characters touched: {chars_touched}",
            f"- Character facts added: {char_facts_added}",
            "",
            "## Details",
        ]

        if world_lines:
            report_lines += ["### World", ""] + world_lines + [""]
        if tl_lines:
            report_lines += ["### Timeline", ""] + tl_lines + [""]
        if char_blocks:
            report_lines += ["### Characters", ""]
            for name, lines in char_blocks:
                report_lines += [f"#### {name}", ""] + lines + [""]

        (approved_dir / "APPROVAL_REPORT.md").write_text(
            "\n".join(report_lines), encoding="utf-8"
        )

    return ApprovalResult(
        run_id=run_id,
        approved_dir=approved_dir,
        world_facts_added=len(world_lines),
        timeline_events_added=len(tl_lines),
        characters_touched=chars_touched,
        character_facts_added=char_facts_added,
    )


# --- compatibility shim -------------------------------------------------------
# The CLI expects approve_run_to_canon(project_dir, run_id, dry_run=False, archive=True).
# If earlier patches introduced a differently named entrypoint, provide a stable alias.

def approve_run_to_canon(project_dir: str, run_id: str, dry_run: bool = False, archive: bool = True):
    """
    Compatibility wrapper expected by CLI.

    The approval implementation in this repo is named `approve_proposals_run` (and sometimes `approve_proposals`).
    This wrapper routes the CLI call to whichever implementation exists.
    """
    # Preferred implementation name (from the ingest-approve patch)
    if "approve_proposals_run" in globals() and callable(globals()["approve_proposals_run"]):
        return globals()["approve_proposals_run"](project_dir=project_dir, run_id=run_id, dry_run=dry_run, archive=archive)

    # Older name (approve a proposals directory rather than a run id)
    if "approve_proposals" in globals() and callable(globals()["approve_proposals"]):
        # This function expects the proposals directory path; construct it from project+run_id
        from pathlib import Path
        proposals_dir = Path(project_dir) / "00_INGEST" / "proposals" / run_id
        return globals()["approve_proposals"](project_dir=project_dir, proposals_dir=proposals_dir, dry_run=dry_run, archive=archive)

    # Legacy names (if present)
    for name in ("approve_to_canon", "approve_run", "approve"):
        if name in globals() and callable(globals()[name]):
            return globals()[name](project_dir=project_dir, run_id=run_id, dry_run=dry_run, archive=archive)

    available = sorted([k for k, v in globals().items() if callable(v)])
    raise RuntimeError(
        "No approve implementation found in storyos.ingest.approve.py. "
        "Expected one of: approve_proposals_run, approve_proposals, approve_to_canon, approve_run, approve. "
        f"Callables available: {available}"
    )

