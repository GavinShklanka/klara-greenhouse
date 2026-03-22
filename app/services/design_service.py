"""Design Service — selects ONE greenhouse type + size recommendation."""

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


def recommend_design(intake: dict, suitability: dict) -> dict:
    """
    Produce ONE greenhouse recommendation based on intake + suitability.
    """
    data = _load_data()
    budget = intake.get("budget", "under_5k")
    goal = intake.get("goal", "grow_food")
    prop = intake.get("property_type", "backyard")
    gh_pref = intake.get("greenhouse_type", "not_sure")
    climate = suitability["climate"]
    budget_ceiling = suitability["budget_ceiling"]

    # --- Step 1: Select greenhouse type ---
    gh_types = data["greenhouse_types"]

    if gh_pref in gh_types and gh_pref != "not_sure":
        selected_type = gh_types[gh_pref]
    else:
        # "not_sure" → engine decides based on budget + goal
        if budget == "under_5k":
            selected_type = gh_types["polytunnel"]
        elif goal in ("sustainability", "save_money") and budget in ("5k_10k", "over_10k"):
            selected_type = gh_types["passive_solar"]
        else:
            selected_type = gh_types["polycarbonate"]

    type_id = selected_type["id"]

    # --- Step 2: Select size tier ---
    cost_matrix = data["cost_matrix"][type_id]
    size_tiers = data["size_tiers"]

    selected_tier = None
    for tier in reversed(size_tiers):
        tier_costs = cost_matrix.get(tier["id"])
        if tier_costs and tier_costs["total_diy_low"] <= budget_ceiling:
            selected_tier = tier
            break

    if selected_tier is None:
        selected_tier = size_tiers[0]

    # Property constraint: backyard caps at "serious"
    if prop == "backyard" and selected_tier["id"] == "market":
        selected_tier = size_tiers[2]

    tier_id = selected_tier["id"]
    costs = cost_matrix[tier_id]

    # --- Step 3: Build decision explanation ---
    goal_labels = {
        "grow_food": "growing your own food year-round",
        "save_money": "reducing grocery costs with high-value crops",
        "sustainability": "sustainable, low-energy food production",
        "mixed": "food production, savings, and sustainability",
    }
    goal_text = goal_labels.get(goal, "your greenhouse goals")

    why = (
        f"A {selected_type['name']} is the best match for your {climate['label']} location "
        f"and {goal_text} goal. {selected_type['description']} "
        f"The {selected_tier['dimensions']} size gives you {selected_tier['beds']} "
        f"with capacity for {selected_tier['capacity']}."
    )

    return {
        "recommendation": f"{selected_tier['dimensions']} {selected_type['name']}",
        "why": why,
        "assumptions": (
            f"Zone {climate['zone']} in {climate['label']}. "
            f"Budget ceiling ~${budget_ceiling:,}. "
            f"Property type: {prop}. "
            f"Snow load: {climate['design_snow_load_psf']} PSF."
        ),
        "next_step": "Review your cost estimate and crop plan below.",
        "greenhouse": {
            "type_id": type_id,
            "type_name": selected_type["name"],
            "type_short": selected_type["short"],
            "description": selected_type["description"],
            "pros": selected_type["pros"],
            "frame": selected_type["frame"],
            "glazing": selected_type["glazing"],
            "r_value": selected_type["r_value"],
            "light_transmission": selected_type["light_transmission"],
        },
        "size": {
            "tier_id": tier_id,
            "label": selected_tier["label"],
            "dimensions": selected_tier["dimensions"],
            "sq_ft": selected_tier["sq_ft"],
            "beds": selected_tier["beds"],
            "capacity": selected_tier["capacity"],
            "best_for": selected_tier["best_for"],
        },
        "climate_context": {
            "zone": climate["zone"],
            "region": climate["label"],
            "last_frost": climate["avg_last_frost"],
            "first_frost": climate["avg_first_frost"],
            "growing_season": climate["growing_season_days"],
            "snow_load": climate["design_snow_load_psf"],
            "frost_depth": climate["frost_depth_inches"],
        },
    }
