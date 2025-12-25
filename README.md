# StoryOS

Local-first, auditable storytelling workflow engine with secure tool use and plugins.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

storyos init my_story --name "My Story"
storyos run my_story --chapter chapter_01 --beat beat_01
```

Outputs:
- Drafts: `04_DRAFTS/`
- Run logs: `05_RUNS/`

## Ingest MVP

```bash
storyos ingest extract examples/demo_project ./examples/demo_project/00_INGEST/inputs/example_source.md
```

Outputs go to `00_INGEST/proposals/<run_id>/` (world, timeline, characters) plus `raw_llm_output.txt` for audit.

## OpenAI adapter

Set your API key in the environment:

```bash
export OPENAI_API_KEY="sk-..."
```

Quick check:

```bash
storyos doctor
```

Ingest uses the OpenAI adapter by default.
