from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from storyos.plugins.manifests import PluginManifest

@dataclass
class PluginRegistry:
    manifests: Dict[str, PluginManifest]

    def get(self, plugin_id: str) -> PluginManifest:
        return self.manifests[plugin_id]

    @staticmethod
    def builtin() -> "PluginRegistry":
        builtins = [
            PluginManifest(id="builtin.planner", kind="agent", permissions=["read_file","search_text"],
                          entrypoint="storyos.builtins.agents.planner:PlannerAgent"),
            PluginManifest(id="builtin.writer", kind="agent", permissions=["read_file"],
                          entrypoint="storyos.builtins.agents.writer:WriterAgent"),
            PluginManifest(id="builtin.continuity", kind="agent", permissions=["read_file"],
                          entrypoint="storyos.builtins.agents.continuity:ContinuityAgent"),
            PluginManifest(id="builtin.voice", kind="agent", permissions=["read_file"],
                          entrypoint="storyos.builtins.agents.voice:VoiceAgent"),
            PluginManifest(id="builtin.librarian", kind="agent", permissions=["read_file","write_file"],
                          entrypoint="storyos.builtins.agents.librarian:LibrarianAgent"),
            PluginManifest(id="builtin.continuity_rules", kind="check", permissions=[],
                          entrypoint="storyos.builtins.checks.continuity_rules:ContinuityRules"),
            PluginManifest(id="builtin.markdown_exporter", kind="exporter", permissions=["write_file"],
                          entrypoint="storyos.builtins.exporters.markdown_exporter:MarkdownExporter"),
        ]
        return PluginRegistry({m.id: m for m in builtins})
