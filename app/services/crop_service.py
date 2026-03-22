"""Crop Plan Service — recommends 3-5 crops based on greenhouse type and goals."""

from __future__ import annotations

import json
from pathlib import Path

_DATA: dict = {}


def _load_data():
    global _DATA
    if not _DATA:
        path = Path(__file__).resolve().parents[2] / "config" / "greenhouse_data.json"
        with open(path, "r", encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


def get_crop_plan(greenhouse_type: str, goal: str, location: str) -> dict:
    """
    Recommend 3-5 crops based on greenhouse type and user goals.
    Rule-based — no ML.
    """
    data = _load_data()
    crops_db = data["crops"]
    climate = data["climate_zones"].get(location, data["climate_zones"]["halifax"])

    recommended = []

    # Always start with high-value, beginner-friendly crops
    # Tomatoes are the #1 greenhouse crop — always include
    tomato = next((c for c in crops_db["warm_season"] if c["name"] == "Tomatoes"), None)
    if tomato:
        recommended.append(tomato)

    # Goal-based selection
    if goal in ("grow_food", "mixed"):
        # Food production focus — add salad greens + cucumbers
        lettuce = next((c for c in crops_db["cool_season"] if "Lettuce" in c["name"]), None)
        if lettuce:
            recommended.append(lettuce)
        cucumber = next((c for c in crops_db["warm_season"] if c["name"] == "Cucumbers"), None)
        if cucumber:
            recommended.append(cucumber)
        kale = next((c for c in crops_db["cool_season"] if c["name"] == "Kale"), None)
        if kale:
            recommended.append(kale)

    elif goal == "save_money":
        # High-value crops that save the most at the grocery store
        peppers = next((c for c in crops_db["warm_season"] if c["name"] == "Peppers"), None)
        if peppers:
            recommended.append(peppers)
        herbs = next((c for c in crops_db["warm_season"] if "Herb" in c["name"]), None)
        if herbs:
            recommended.append(herbs)
        lettuce = next((c for c in crops_db["cool_season"] if "Lettuce" in c["name"]), None)
        if lettuce:
            recommended.append(lettuce)

    elif goal == "sustainability":
        # Year-round production focus
        kale = next((c for c in crops_db["cool_season"] if c["name"] == "Kale"), None)
        if kale:
            recommended.append(kale)
        lettuce = next((c for c in crops_db["cool_season"] if "Lettuce" in c["name"]), None)
        if lettuce:
            recommended.append(lettuce)
        garlic = next((c for c in crops_db["winter_greenhouse"] if "Garlic" in c["name"]), None)
        if garlic:
            recommended.append(garlic)

    # Passive solar or food goal → add a winter crop
    if greenhouse_type == "passive_solar" or goal in ("grow_food", "sustainability"):
        winter_lettuce = next((c for c in crops_db["winter_greenhouse"] if "Winter" in c["name"]), None)
        if winter_lettuce and winter_lettuce not in recommended:
            recommended.append(winter_lettuce)

    # Cap at 5
    recommended = recommended[:5]

    # Build seasonal timeline
    seasons = {
        "spring": [c["name"] for c in recommended if "March" in c.get("start_indoor", "") or "April" in c.get("start_indoor", "")],
        "summer": [c["name"] for c in recommended if any(m in c.get("harvest_months", "") for m in ["Jul", "Aug"])],
        "fall": [c["name"] for c in recommended if any(m in c.get("harvest_months", "") for m in ["Sep", "Oct", "Nov"])],
        "winter": [c["name"] for c in recommended if any(m in c.get("harvest_months", "") for m in ["Dec", "Jan", "Feb", "Mar"])],
    }

    return {
        "recommendation": f"{len(recommended)} crops selected for your greenhouse",
        "why": (
            f"These crops are selected for {climate['label']} conditions "
            f"(Zone {climate['zone']}, {climate['growing_season_days']}-day outdoor season). "
            f"A greenhouse extends this dramatically — most of these can produce 8-10 months per year."
        ),
        "assumptions": (
            f"Based on a {greenhouse_type} greenhouse in {climate['label']}. "
            f"All recommended crops are rated beginner or intermediate difficulty."
        ),
        "next_step": "Your full plan includes planting schedules and spacing guides for each crop.",
        "crops": [
            {
                "name": c["name"],
                "difficulty": c["difficulty"],
                "harvest_months": c["harvest_months"],
                "note": c["note"],
                "yield_per_plant": c.get("yield_per_plant", "varies"),
            }
            for c in recommended
        ],
        "seasonal_timeline": seasons,
    }
