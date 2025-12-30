from __future__ import annotations

import typer
from rich.console import Console

from storyos.core.workspace import Workspace
from storyos.workflow.engine import WorkflowEngine
from storyos.config import load_project_config

app = typer.Typer(add_completion=False)

ingest_app = typer.Typer(add_completion=False)
app.add_typer(ingest_app, name="ingest")
console = Console()


@app.command()
def run(
    project_dir: str = typer.Argument(..., help="Path to a StoryOS MPF project folder"),
    chapter: str = typer.Option("chapter_01", help="Chapter id/name (e.g., chapter_01)"),
    beat: str = typer.Option("beat_01", help="Beat id/name (e.g., beat_02)"),
):
    """Run the storytelling pipeline for a specific chapter + beat."""
    cfg = load_project_config(project_dir)
    ws = Workspace.open(project_dir=project_dir, config=cfg)

    engine = WorkflowEngine.from_config(cfg, ws)
    result = engine.run(chapter=chapter, beat=beat)

    console.print(f"[bold green]Done.[/bold green] Run id: {result.run_id}")
    console.print(f"Draft: {result.outputs.get('draft_path', '(none)')}")
    console.print(f"Run log: {result.outputs.get('runlog_path', '(none)')}")


@ingest_app.command("extract")
def ingest_extract(
    project_dir: str = typer.Argument(..., help="Path to an MPF project folder"),
    input_path: str = typer.Argument(..., help="Path to a text/markdown file to ingest"),
    max_lines: int = typer.Option(80, help="Max lines per chunk"),
    overlap: int = typer.Option(10, help="Overlap lines between chunks"),
):
    """Extract proposals (world/timeline/characters) into 00_INGEST/proposals/<run_id>/."""
    from storyos.ingest.extract import extract_to_proposals
    result = extract_to_proposals(
        project_dir=project_dir,
        input_path=input_path,
        max_lines_per_chunk=max_lines,
        overlap=overlap,
    )
    console.print(f"[bold green]Extracted proposals.[/bold green] Run id: {result.run_id}")
    console.print(f"Proposals: {result.proposals_dir}")

@ingest_app.command("approve")
def ingest_approve(
    project_dir: str = typer.Argument(..., help="Path to a StoryOS project folder"),
    run_id: str = typer.Argument(..., help="Run id under 00_INGEST/proposals/<run_id>"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
    archive: bool = typer.Option(True, help="Move approved proposals to 00_INGEST/approved/<run_id>"),
):
    # Import inside to keep CLI import-time light.
    from storyos.ingest.approve import approve_run_to_canon

    result = approve_run_to_canon(
        project_dir=project_dir,
        run_id=run_id,
        dry_run=dry_run,
        archive=archive,
    )
    console.print("✅ Approved ingest run")
    console.print(f"  Run: {run_id}")
    console.print(f"  Report: {getattr(result, 'report_path', None)}")
    if dry_run:
        console.print("  (dry-run: nothing was written)")


@app.command()
def init(
    target_dir: str = typer.Argument(..., help="Where to create a new MPF project"),
    name: str = typer.Option("My Story", help="Project name"),
):
    """Create a new MPF project skeleton."""
    Workspace.init_project(target_dir=target_dir, name=name)
    console.print(f"[bold green]Created.[/bold green] {target_dir}")



@app.command()
def doctor():
    """Quick environment sanity checks."""
    import os
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    console.print(f"OPENAI_API_KEY set: {'yes' if has_key else 'no'}")
    if not has_key:
        raise typer.Exit(code=2)
    try:
        from storyos.llm.openai_adapter import OpenAIAdapter
        from storyos.llm.base import LLMMessage
        a = OpenAIAdapter()
        r = a.generate([LLMMessage(role="user", content="Say 'ok'")], model="gpt-4.1-mini", temperature=0)
        console.print(f"OpenAI call: {r.text.strip()}")
    except Exception as e:
        console.print(f"[bold red]OpenAI call failed:[/bold red] {e}")
        raise typer.Exit(code=3)


if __name__ == "__main__":
    app()
