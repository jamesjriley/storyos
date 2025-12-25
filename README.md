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
