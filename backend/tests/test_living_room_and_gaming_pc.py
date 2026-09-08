"""
Scripted runs of the living room and gaming PC scenarios, including the conditional
branches (RGB kit, keyboard/mouse) that the dining table scenario doesn't exercise.

Run with: python -m tests.test_living_room_and_gaming_pc
Requires the server running locally and seed_data_living_room_gaming_pc.sql applied.
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


def run_living_room_scenario() -> None:
    reply = _run_conversation([
        "I want to furnish my living room.",
        "12ft x 14ft",
        "medium",
        "modern",
        "4",
    ])
    assert reply["is_final"] is True
    names = {item["name"] for item in reply["shopping_list"]}
    expected = {
        "Sofa Set", "Coffee Table", "TV Unit", "Curtains", "Carpet",
        "Floor Lamp", "Wall Decor", "Indoor Plants",
    }
    missing = expected - names
    assert not missing, f"Missing expected items: {missing}"
    print("Living room scenario PASSED.\n")


def run_gaming_pc_scenario_with_accessories_and_rgb() -> None:
    """Customer already has accessories and does NOT want RGB -> no keyboard/mouse/RGB kit."""
    reply = _run_conversation([
        "I want to build a gaming PC.",
        "mid-range",
        "competitive shooters and streaming",
        "no",
        "yes",  # has_accessories = yes -> keyboard/mouse should be excluded
    ])
    assert reply["is_final"] is True
    names = {item["name"] for item in reply["shopping_list"]}
    core = {"Processor (CPU)", "Motherboard", "RAM", "Graphics Card (GPU)", "SSD", "Power Supply", "PC Cabinet", "Cooling Fan"}
    assert core.issubset(names), f"Missing core components: {core - names}"
    assert "Keyboard" not in names, "Keyboard should be excluded when has_accessories=yes"
    assert "Mouse" not in names, "Mouse should be excluded when has_accessories=yes"
    assert "RGB Lighting Kit" not in names, "RGB kit should be excluded when rgb=no"
    print("Gaming PC scenario (has accessories, no RGB) PASSED.\n")


def run_gaming_pc_scenario_needs_accessories_and_rgb() -> None:
    """Customer wants RGB and does NOT already have accessories -> keyboard/mouse/RGB kit included."""
    reply = _run_conversation([
        "I want to build a gaming PC.",
        "high-end",
        "AAA gaming at 4K",
        "yes",
        "no",  # has_accessories = no -> keyboard/mouse should be included
    ])
    assert reply["is_final"] is True
    names = {item["name"] for item in reply["shopping_list"]}
    assert "Keyboard" in names, "Keyboard should be included when has_accessories=no"
    assert "Mouse" in names, "Mouse should be included when has_accessories=no"
    assert "RGB Lighting Kit" in names, "RGB kit should be included when rgb=yes"
    print("Gaming PC scenario (needs accessories, wants RGB) PASSED.\n")


if __name__ == "__main__":
    run_living_room_scenario()
    run_gaming_pc_scenario_with_accessories_and_rgb()
    run_gaming_pc_scenario_needs_accessories_and_rgb()
