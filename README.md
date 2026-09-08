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
   the final shopping list from a product-relationships table in Postgres.
5. The LLM writes a short friendly intro for the already-assembled list — it cannot add,
   remove, or invent items at this stage.

This split matters: every recommended item traces back to a row in the database, so the
recommendation logic is fully explainable and can't hallucinate a product that doesn't exist
in the catalog.

## Tech stack
- **Frontend:** Next.js (App Router) + Tailwind
- **Backend:** FastAPI
- **Database:** Supabase (Postgres)
- **LLM:** Ollama Cloud, `gpt-oss:120b`

## Project structure
```
backend/
  app/
    main.py            FastAPI entrypoint, CORS, /health
    config.py           env settings
    db.py                SQLAlchemy engine/session
    models.py            ORM tables: categories, category_questions, products, product_relationships
    schemas.py            Pydantic request/response models
    routers/chat.py       the /chat endpoint — the conversation state machine
    services/
      llm_service.py       Ollama calls: classify_category, extract_field, narrate_list
      recommendation_service.py   deterministic SQL shopping-list builder
      session_service.py    in-memory per-session state
  seed/seed_data.sql    seed data for the dining table + TV mount scenarios
  scripts/create_tables.py   one-off table creation from models.py
  tests/test_scenarios.py    scripted end-to-end run of the dining table scenario
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
  This creates the tables from `app/models.py`.
- Run `seed/seed_data.sql` in the Supabase SQL editor to load the dining table and TV mount scenarios.

### 2. Backend
```
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, OLLAMA_BASE_URL, OLLAMA_API_KEY
uvicorn app.main:app --reload --port 8000
```
Check `http://localhost:8000/health` returns `{"status": "ok", "database": "ok"}`.

### 3. Frontend
```
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir   # if not already scaffolded
npm install
cp .env.local.example .env.local
npm run dev
```
Open `http://localhost:3000`.

### 4. Verify end-to-end
```
cd backend
python -m tests.test_scenarios
```
This runs the full dining table conversation against your local server and checks the
final shopping list matches the expected 7 items.

## AI usage note
We used an AI assistant to scaffold the FastAPI service layer, database schema, and
Next.js chat UI. At runtime, Ollama Cloud (`gpt-oss:120b`) is used only for category
classification, field extraction from free text, and phrasing the final list — all
actual product recommendations come from deterministic SQL against the
`product_relationships` table, not from the LLM.
