from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from storyos.config import ProjectConfig

class WorkspaceError(Exception):
    pass

@dataclass
class Workspace:
    root: Path
    config: ProjectConfig

    @classmethod
    def open(cls, project_dir: str, config: ProjectConfig) -> "Workspace":
        root = Path(project_dir).resolve()
        if not (root / "project.yaml").exists():
            raise WorkspaceError("Not an MPF project: missing project.yaml")
        return cls(root=root, config=config)

    @staticmethod
    def init_project(target_dir: str, name: str) -> None:
        root = Path(target_dir)
        root.mkdir(parents=True, exist_ok=True)

        for d in ["00_INGEST/inputs","00_INGEST/proposals","01_CANON","02_CHARACTERS","03_OUTLINES","04_DRAFTS","05_RUNS","06_EXPORTS"]:
            (root/d).mkdir(exist_ok=True)

        (root / "project.yaml").write_text(
            f'''project:
  name: "{name}"
  version: "0.1"
  default_pov: "third_tight"
  target_beat_words: 950

security:
  allow_cloud_models: true
  allowed_workspace_roots:
    - "."
  max_file_read_kb: 256
  max_file_write_kb: 512

llm:
  provider: "openai"
  model: "gpt-4.1-mini"
  temperature: 0.8

workflow:
  steps:
    - load_context
    - retrieve_canon
    - plan_beat
    - draft_beat
    - continuity_check
    - voice_pass
    - user_review_gate
    - write_outputs
    - write_runlog

plugins:
  enabled:
    agents:
      - "builtin.planner"
      - "builtin.writer"
      - "builtin.continuity"
      - "builtin.voice"
      - "builtin.librarian"
    checks:
      - "builtin.continuity_rules"
    exporters:
      - "builtin.markdown_exporter"
''',
            encoding="utf-8",
        )

        (root / "00_README.md").write_text(
            "# StoryOS Project\n\nThis is a human-readable MPF workspace.\n\n## Ingest\n\n- Put raw text into 00_INGEST/inputs/ and run `storyos ingest extract`.\n",
            encoding="utf-8",
        )

    def safe_path(self, rel_path: str) -> Path:
        candidate = (self.root / rel_path).resolve()
        if not str(candidate).startswith(str(self.root)):
            raise WorkspaceError(f"Path escapes workspace: {rel_path}")
        return candidate
