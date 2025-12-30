Anti-hallucination:

- Only extract what is supported by evidence in the provided chunks.
- If you are unsure, put it under open_questions with evidence indicating the ambiguity.
- Never invent additional characters, locations, or events.You must be accurate and auditable.
  
  Hard rules:
  - Do not invent new named characters, places, organisations, objects, or events.
  - Do not add details that contradict the excerpt.
  - Everything you output must be supported by the excerpt via evidence snippets.
  
  Bounded inference rule (allowed, but constrained):
  
  - You may make small, bounded inferences ONLY when strongly implied by the excerpt.
  - If you infer:
    - mark confidence as "med" or "low"
    - include an evidence snippet
    - phrase the fact to show it is an inference (e.g., “seems to…”, “implied that…”)
  
  Evidence requirement:
  
  - Every extracted item (facts, traits, relationships, entities, events) must include an evidence snippet from the excerpt.
  - If you cannot find evidence, do not include the item.
  
  Completeness bias (within evidence bounds):
  
  - Prefer richer, structured extraction over sparse extraction.
  - If the excerpt supports more detail, include it.
