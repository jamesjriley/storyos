# Ingest approval workflow

## Goal

`storyos ingest extract` is intentionally "hands-off": it writes **proposals** (draft canon) into `00_INGEST/proposals/<run_id>/`.

`storyos ingest approve` is the second half: it **merges** a chosen proposal run into your human-audited canon:

- `01_CANON/world.md`
- `01_CANON/timeline.md`
- `02_CHARACTERS/*.md`

Everything is stamped with provenance (`ingest <run_id>` + UTC timestamp) so you can always see where a fact came from.

## What files matter (and why)

For each run id under `00_INGEST/proposals/<run_id>/`:

- `raw_llm_output.txt` (important)
  - The machine output (JSON). This is the *source of truth* for approval.
- `world.md`, `timeline.md`, `characters/*.md` (helpful)
  - Human-readable previews generated from the same JSON.

After approval, a report is written:

- `00_INGEST/approved/<run_id>/APPROVAL_REPORT.md` (important)
  - What was merged, where, and how many items.

## How to use it

Preview changes (no writes):

```bash
storyos ingest approve examples/demo_project 2025-12-26_21-04-00__ingest__02108f --dry-run
```

Apply changes and archive the proposals:

```bash
storyos ingest approve examples/demo_project 2025-12-26_21-04-00__ingest__02108f
```

## Maintenance rules (recommended)

- Treat `01_CANON/` + `02_CHARACTERS/` as your **single source of truth**.
- Never edit `00_INGEST/proposals/` in place. Either:
  - re-run extract, or
  - approve and then edit the canon files.
- Keep `00_INGEST/approved/` around for auditability.
- If you later want automated deduping/conflict resolution, add it **in approval** (not extract).

## Notes on the merge strategy

This implementation is conservative:

- It appends new sections rather than trying to rewrite existing canon.
- It does not delete or overwrite facts.
- Confidences are normalised to: `high | med | low`.

If you want stricter behaviour (dedupe, conflict checks, blocking low-confidence items, interactive approval), this is the right place to extend.
