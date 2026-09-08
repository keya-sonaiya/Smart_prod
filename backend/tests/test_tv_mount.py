"""
Scripted runs of the TV mount scenario, including its one conditional branch
(Cable Management Kit only appears when cable_mgmt = yes).

Run with: python -m tests.test_tv_mount
Requires the server running locally and seed_data.sql applied.
"""
import uuid

import httpx

BASE_URL = "http://localhost:8000"


def _run_conversation(turns: list[str]) -> dict:
    session_id = str(uuid.uuid4())
    reply = None
    for turn in turns:
        resp = httpx.post(f"{BASE_URL}/chat", json={"session_id": session_id, "message": turn}, timeout=30)
        resp.raise_for_status()
        reply = resp.json()
        print(f"> {turn}\n< {reply['reply']}\n")
    assert reply is not None
    return reply


def run_tv_mount_with_cable_management() -> None:
    reply = _run_conversation([
        "I want to mount my TV on the wall.",
        "55",
        "drywall",
        "adjustable",
        "yes",  # cable_mgmt = yes -> Cable Management Kit should be included
    ])
    assert reply["is_final"] is True
    names = {item["name"] for item in reply["shopping_list"]}
    core = {"TV Wall Mount", "Wall Plugs", "Screws & Bolts", "Drill Machine", "Spirit Level"}
    missing = core - names
    assert not missing, f"Missing core items: {missing}"
    assert "Cable Management Kit" in names, "Cable Management Kit should appear when cable_mgmt=yes"
    print("TV mount scenario (with cable management) PASSED.\n")


def run_tv_mount_without_cable_management() -> None:
    reply = _run_conversation([
        "I want to mount my TV on the wall.",
        "65",
        "concrete",
        "fixed",
        "no",  # cable_mgmt = no -> Cable Management Kit should be excluded
    ])
    assert reply["is_final"] is True
    names = {item["name"] for item in reply["shopping_list"]}
    core = {"TV Wall Mount", "Wall Plugs", "Screws & Bolts", "Drill Machine", "Spirit Level"}
    missing = core - names
    assert not missing, f"Missing core items: {missing}"
    assert "Cable Management Kit" not in names, "Cable Management Kit should be excluded when cable_mgmt=no"
    print("TV mount scenario (without cable management) PASSED.\n")


if __name__ == "__main__":
    run_tv_mount_with_cable_management()
    run_tv_mount_without_cable_management()
