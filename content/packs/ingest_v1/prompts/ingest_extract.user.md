INPUT FILE: {{filename}}

{{chunk_text}}

You are ingesting a text excerpt from a story/book and extracting a structured “proposal” for a StoryOS world model.

INPUT TEXT:
---

{{INPUT_TEXT}}
---

Output must be valid JSON that conforms to the provided schema.

Quality + coverage requirements:

- Be comprehensive. Do not stop after 1–2 facts.
- Extract ALL named and clearly implied characters present in the text excerpt.
- For each character, produce:
  - At least 8 facts if the excerpt supports it (otherwise: as many as supported, but try hard).
  - Traits (behavioural/personality) where supported.
  - Relationships with other characters where supported.
  - Preferences (likes/dislikes), goals/motivations, and fears/constraints where supported.
- Extract entities (objects, places, organisations, important items) that matter in the excerpt.
- Extract timeline events / beats:
  - Prefer multiple small events over one vague event.
  - Each event should list participants and any relevant entities/locations.

Evidence + confidence:

- Every fact / trait / relationship / entity / event must include an evidence snippet from the text.
- If something is strongly implied (not explicitly stated), you may include it but:
  - set confidence to "med" or "low"
  - include evidence and explain the inference briefly in the fact text
- Never invent new named characters, places, or events that are not supported by the excerpt.

Formatting:

- Return JSON only. No markdown, no commentary, no code fences.
