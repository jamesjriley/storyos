from __future__ import annotations
from typing import Any, Dict
from storyos.config import ProjectConfig
from storyos.core.workspace import Workspace
from storyos.plugins.registry import PluginRegistry
from storyos.plugins.loader import load_entrypoint
from storyos.tools.file_tools import FileTools

def load_context_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    ft = FileTools(ws)
    chapter_file = f"03_OUTLINES/{ctx['chapter']}.md"
    if ws.safe_path(chapter_file).exists():
        ctx["chapter_outline"] = ft.read_file(chapter_file, ctx["policy"].max_file_read_bytes)
        ctx["runlog"].file_access.append({"path": chapter_file, "action": "read"})
    else:
        ctx["chapter_outline"] = ""

def retrieve_canon_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    ft = FileTools(ws)
    canon_files = ["01_CANON/world.md", "01_CANON/timeline.md", "01_CANON/rules.md"]
    canon = []
    for f in canon_files:
        p = ws.safe_path(f)
        if p.exists():
            canon.append(ft.read_file(f, ctx["policy"].max_file_read_bytes))
            ctx["runlog"].file_access.append({"path": f, "action": "read"})
    ctx["canon_bundle"] = "\n\n---\n\n".join(canon)

def plan_beat_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    Planner = load_entrypoint(registry.get("builtin.planner").entrypoint)
    ctx["beat_plan"] = Planner().run(cfg, ws, ctx)

def draft_beat_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    Writer = load_entrypoint(registry.get("builtin.writer").entrypoint)
    ctx["draft_text"] = Writer().run(cfg, ws, ctx)

def continuity_check_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    Continuity = load_entrypoint(registry.get("builtin.continuity").entrypoint)
    ctx["continuity_report"] = Continuity().run(cfg, ws, ctx)

def voice_pass_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    Voice = load_entrypoint(registry.get("builtin.voice").entrypoint)
    ctx["voice_text"] = Voice().run(cfg, ws, ctx)

def user_review_gate_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    ctx["approved_text"] = ctx.get("voice_text") or ctx.get("draft_text") or ""

def write_outputs_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    ft = FileTools(ws)
    run_id = ctx["runlog"].run_id
    out_path = f"04_DRAFTS/{ctx['chapter']}_{ctx['beat']}_{run_id}.md"
    ft.write_file(out_path, ctx["approved_text"], ctx["policy"].max_file_write_bytes)
    ctx["runlog"].file_access.append({"path": out_path, "action": "write"})
    ctx["runlog"].outputs["draft_path"] = out_path

def write_runlog_step(cfg: ProjectConfig, ws: Workspace, registry: PluginRegistry, ctx: Dict[str, Any]) -> None:
    ft = FileTools(ws)
    run_id = ctx["runlog"].run_id
    log_path = f"05_RUNS/{run_id}.yaml"
    ft.write_file(log_path, ctx["runlog"].to_yaml(), ctx["policy"].max_file_write_bytes)
    ctx["runlog"].file_access.append({"path": log_path, "action": "write"})
    ctx["runlog"].outputs["runlog_path"] = log_path
