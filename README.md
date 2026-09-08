# Smart Product Recommendation Assistant

An AI-guided chat assistant that takes a customer from "I want to build a dining table"
to a complete, quantity-accurate shopping list — without waiting for a human expert.

## How it works

1. The customer describes what they want in free text.
2. The LLM (Ollama Cloud, `gpt-oss:120b`) classifies the request into one of our known
   categories, or flags it as `unknown` for human handoff.
3. The assistant asks the category's follow-up questions one at a time; the LLM extracts
   structured answers from free-text replies.
4. Once all answers are collected, **a deterministic SQL query** (not the LLM) assembles
   the final shopping list from a product-relationships table in Postgres, including any
   conditional items (e.g. cable management only if requested, RGB kit only if requested).
5. The LLM writes a short friendly intro for the already-assembled list — it cannot add,
   remove, or invent items at this stage.

This split matters: every recommended item traces back to a row in the database, so the
recommendation logic is fully explainable and can't hallucinate a product that doesn't exist
in the catalog. See `DECISIONS.md` for the reasoning behind this and other choices.

## Tech stack
- **Frontend:** Next.js (App Router) + Tailwind
- **Backend:** FastAPI
- **Database:** Supabase (Postgres)
- **LLM:** Ollama Cloud, `gpt-oss:120b`

## Scenarios covered
| Scenario | Conditional logic exercised |
|---|---|
| Dining table | Wood-only accessory items (glue, sandpaper, polish, screws) |
| TV wall mount | Cable Management Kit only if requested |
| Living room furnishing | — (core vs. optional item split) |
| Gaming PC | Keyboard/Mouse only if not already owned; RGB Kit only if requested |

## Project structure
```
backend/
  app/
    main.py              FastAPI entrypoint, CORS, /health
    config.py             env settings
    db.py                  SQLAlchemy engine/session
    models.py              ORM tables: categories, category_questions, products, product_relationships
    schemas.py              Pydantic request/response models
    routers/chat.py         the /chat endpoint — the conversation state machine
    services/
      llm_service.py         Ollama calls: classify_category, extract_field, narrate_list
      recommendation_service.py  deterministic SQL shopping-list builder
      session_service.py      per-session state, persisted in the conversation_sessions table
  seed/
    seed_data.sql                       dining table + TV mount
    seed_data_living_room_gaming_pc.sql  living room + gaming PC
  scripts/create_tables.py   one-off table creation from models.py
  tests/
    test_scenarios.py                    dining table, end-to-end
    test_tv_mount.py                     TV mount, both cable-mgmt branches
    test_living_room_and_gaming_pc.py    living room + both gaming PC branches
frontend/
  app/                  Next.js App Router pages
  components/           ChatWindow, MessageBubble, ShoppingListCard
  lib/api.ts             fetch wrapper to the FastAPI backend
```

## How to run

### 1. Database
- Create a Supabase project, copy the pooled connection string.
- From `backend/`, run:
  ```
  python -m scripts.create_tables
  ```
- Run **both** seed files in the Supabase SQL editor, in order:
  1. `seed/seed_data.sql`
  2. `seed/seed_data_living_room_gaming_pc.sql`

### 2. Backend
```
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, OLLAMA_BASE_URL, OLLAMA_API_KEY
uvicorn app.main:app --reload --port 8000
```
Check `http://localhost:8000/health` returns `{"status": "ok", "database": "ok", "llm": "ok"}`.

### 3. Frontend
```
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Open `http://localhost:3000`.

### 4. Verify end-to-end (all 4 scenarios, run with the server up)
```
cd backend
python -m tests.test_scenarios
python -m tests.test_tv_mount
python -m tests.test_living_room_and_gaming_pc
```
All three should print `PASSED` for every scenario, including both directions of each
conditional branch (cable management on/off, RGB + accessories on/off).

## AI usage note
We used an AI assistant to scaffold the FastAPI service layer, database schema, seed
data, test scripts, and Next.js chat UI. At runtime, Ollama Cloud (`gpt-oss:120b`) is
used only for category classification, field extraction from free text, and phrasing
the final list — all actual product recommendations come from deterministic SQL
against the `product_relationships` table, not from the LLM. During testing we caught
and fixed a case where the narration step leaked its own raw input back into the
reply; see `DECISIONS.md` for details.