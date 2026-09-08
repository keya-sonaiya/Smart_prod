# Decision Log

- The LLM only classifies category, extracts structured fields, and narrates an
  already-built list — it never decides what to recommend. Every recommended item
  traces to a row in `product_relationships`, which makes the system fully
  explainable and avoids hallucinated products.
- All LLM calls run at `temperature: 0` and require raw JSON output; every response
  is re-validated against our own known values (category keys, enum options, numeric
  types) before being trusted — the model's constraint-following is a hint, not a guarantee.
- Quantity formulas are resolved through a small whitelisted lookup (`_NAMED_FORMULAS`),
  never `eval()`, to avoid arbitrary code execution risk from any upstream text.
- Used a single `product_relationships` table with `relation_type` + `condition_json`
  instead of a graph database — enough to express REQUIRES/OPTIONAL and
  conditional branches (material, budget, RGB, existing accessories) without the
  setup cost of a graph DB under time pressure.
- Session state is an in-memory dict, not Redis or a DB table — sufficient for a
  demo, but would not survive a server restart or scale past one process.
- Seeded exactly the 4 example scenarios from the problem statement (dining table,
  TV mount, living room, gaming PC) rather than a broad general catalog. Depth and
  correctness — including conditional branching — mattered more than breadth in a
  3-hour build. The schema adds new categories with zero code changes (seed rows only),
  so this is a scope choice, not a technical ceiling.
- Every scenario is covered by a scripted end-to-end test (`tests/test_scenarios.py`,
  `test_tv_mount.py`, `test_living_room_and_gaming_pc.py`), and the two scenarios with
  conditional items (TV mount's Cable Management Kit, gaming PC's Keyboard/Mouse/RGB Kit)
  are each tested in both directions to prove the conditions actually gate the output,
  not just that a fixed list comes back.
- Found and fixed a real LLM behavior during testing: `narrate_list` initially echoed
  the raw item list (including the literal words "Category:" / "Items:") back into its
  reply instead of writing only an intro. Fixed with a tighter system prompt plus a
  defensive string-truncation fallback in code, since prompt instructions alone aren't
  a guarantee the model follows them.
- `narrate_list` also degrades gracefully to a static sentence if the Ollama call
  itself fails, so a flaky LLM call can't block the customer from seeing their
  shopping list — the list itself is unaffected either way since it's built by SQL.
- Answers that currently change the output: dining-table seating scales nut-and-bolt
  quantity; TV wall type removes toggle hardware for drywall and mount type adds an
  adjustable arm; living-room budget gates optional decor and occupants over four
  doubles curtains and carpet; gaming-PC budget selects RTX 4060/4070/4090 and adds
  a second SSD for high-end builds; RGB, existing accessories, material, and cable
  management also gate their related items. Room size, TV size, gaming usage, style,
  and most free-text answers are collected for context but do not yet affect the list.
- With more time: add pgvector embeddings for semantic category matching on ambiguous
  input, support mid-flow corrections ("actually I meant metal, not wood"), add a
  human-handoff queue for `unknown` classifications instead of a dead-end message, and
  persist session state to the DB instead of an in-memory dict.