"""
Scripted run of the dining table scenario against a live server.
Requires the app running locally (uvicorn app.main:app --port 8000) and seed_data.sql applied.

Run with: python -m tests.test_scenarios
"""
import uuid

import httpx

BASE_URL = "http://localhost:8000"


def run_dining_table_scenario() -> None:
    session_id = str(uuid.uuid4())
    turns = [
        "I want to build a dining table.",
        "4 ft x 6 ft",
        "wood",
        "6",
    ]

    reply = None
    for turn in turns:
        resp = httpx.post(f"{BASE_URL}/chat", json={"session_id": session_id, "message": turn}, timeout=30)
        resp.raise_for_status()
        reply = resp.json()
        print(f"> {turn}\n< {reply['reply']}\n")

    assert reply is not None
    assert reply["is_final"] is True, "Expected a final shopping list after 4 turns"
    names = {item["name"] for item in reply["shopping_list"]}
    expected = {
        "Wooden Sheet", "Table Legs", "Nut & Bolt Set", "Wood Screws",
        "Wood Glue", "Sandpaper", "Wood Polish",
    }
    missing = expected - names
    assert not missing, f"Missing expected items: {missing}"
    print("Dining table scenario PASSED.")


def run_dining_table_scenario_large_seating() -> None:
    """seating=10 -> Nut & Bolt Set quantity should scale to seating/2."""
    session_id = str(uuid.uuid4())
    turns = ["I want to build a dining table.", "4x6", "wood", "10"]
    reply = None
    for turn in turns:
        response = httpx.post(
            f"{BASE_URL}/chat",
            json={"session_id": session_id, "message": turn},
            timeout=30,
        )
        response.raise_for_status()
        reply = response.json()
    assert reply is not None and reply["is_final"] is True
    bolt_qty = next(item["quantity"] for item in reply["shopping_list"] if item["name"] == "Nut & Bolt Set")
    assert bolt_qty == 5, f"Expected 5, got {bolt_qty}"
    print("Dining table large-seating quantity scenario PASSED.")


if __name__ == "__main__":
    run_dining_table_scenario()
    run_dining_table_scenario_large_seating()
