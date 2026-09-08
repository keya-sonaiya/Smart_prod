"""
Run once, before seed_data.sql:

    cd backend
    python -m scripts.create_tables

Creates all tables defined in app/models.py against DATABASE_URL from .env.
"""
from app import models  # noqa: F401  (import registers the models on Base.metadata)
from app.db import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
