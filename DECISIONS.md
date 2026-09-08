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
  material-conditional branches without the setup cost of Neo4j under time pressure.
- Session state is an in-memory dict, not Redis or a DB table — sufficient for a
  demo, but would not survive a server restart or scale past one process.
- Seeded only 2 categories fully (dining table, TV mount) to get one end-to-end path
  rock-solid before replicating the pattern to living room / gaming PC — the schema
  supports more without code changes, only more seed rows.
- `narrate_list` degrades gracefully to a static sentence if the Ollama call fails,
  so a flaky LLM call can't block the customer from seeing their shopping list.
- With more time: add pgvector embeddings for semantic category matching on ambiguous
  input, support mid-flow corrections ("actually I meant metal, not wood"), and add a
  human-handoff queue for `unknown` classifications instead of a dead-end message.
