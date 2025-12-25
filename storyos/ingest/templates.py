from __future__ import annotations
from storyos.ingest.schemas import ProposedCharacter, ProposedWorld, ProposedTimeline

def _ev(evs):
    if not evs: return ""
    lines=[]
    for ev in evs:
        note = f" — {ev.note}" if getattr(ev, "note", "") else ""
        lines.append(f"- [source: {ev.source}]{note}")
    return "\n".join(lines)

def render_character_md(ch: ProposedCharacter) -> str:
    lines=[f"# Proposed Character: {ch.name}","", "## Facts (proposed)"]
    if not ch.facts: lines.append("- (none)")
    for f in ch.facts:
        lines.append(f"- {f.claim}  (confidence: {f.confidence})")
        ev=_ev(f.evidence)
        if ev: lines.append(ev)
    lines += ["", "## Open questions"]
    if not ch.open_questions: lines.append("- (none)")
    for q in ch.open_questions:
        lines.append(f"- {q.question}")
        ev=_ev(q.evidence)
        if ev: lines.append(ev)
    lines.append("")
    return "\n".join(lines)

def render_world_md(world: ProposedWorld) -> str:
    lines=["# Proposed World Facts","", "## Facts (proposed)"]
    if not world.facts: lines.append("- (none)")
    for f in world.facts:
        lines.append(f"- {f.claim}  (confidence: {f.confidence})")
        ev=_ev(f.evidence)
        if ev: lines.append(ev)
    lines += ["", "## Open questions"]
    if not world.open_questions: lines.append("- (none)")
    for q in world.open_questions:
        lines.append(f"- {q.question}")
        ev=_ev(q.evidence)
        if ev: lines.append(ev)
    lines.append("")
    return "\n".join(lines)

def render_timeline_md(tl: ProposedTimeline) -> str:
    lines=["# Proposed Timeline",""]
    if not tl.events: lines.append("- (none)")
    for e in tl.events:
        lines.append(f"- **{e.when}** — {e.what}  (confidence: {e.confidence})")
        ev=_ev(e.evidence)
        if ev: lines.append(ev)
    lines.append("")
    return "\n".join(lines)
