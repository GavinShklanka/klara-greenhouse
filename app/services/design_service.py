"""Design Service — selects ONE greenhouse type + size recommendation."""

from __future__ import annotations

from app.core.data_loader import get_greenhouse_data


def recommend_design(intake: dict, suitability: dict) -> dict:
    """
    Produce ONE greenhouse recommendation based on intake + suitability.
    """
    data = get_greenhouse_data()
    budget = intake.get("budget", "under_5k")
    goal = intake.get("goal", "grow_food")
    prop = intake.get("property_type", "backyard")
    gh_pref = intake.get("greenhouse_type", "not_sure")
    climate = suitability["climate"]
    budget_ceiling = suitability["budget_ceiling"]

    trace = []
    trace.append(f"Location: {climate['label']} (Zone {climate['zone']})")
    trace.append(f"Budget Ceiling: ${budget_ceiling:,}")

    # --- Step 1: Select greenhouse type ---
    gh_types = data["greenhouse_types"]

    if gh_pref in gh_types and gh_pref != "not_sure":
        selected_type = gh_types[gh_pref]
        trace.append(f"Type: User explicitly preferred '{gh_pref}'")
    else:
        # "not_sure" → engine decides based on budget + goal
        if budget == "under_5k":
            selected_type = gh_types["polytunnel"]
            trace.append("Type: Selected Polytunnel due to budget < $5k")
        elif goal in ("sustainability", "save_money") and budget in ("5k_10k", "over_10k"):
            selected_type = gh_types["passive_solar"]
            trace.append(f"Type: Selected Passive Solar due to goal '{goal}' and budget '{budget}'")
        else:
            selected_type = gh_types["polycarbonate"]
            trace.append("Type: Defaulted to Polycarbonate for mid-range budget/standard goal")

    type_id = selected_type["id"]

    # --- Step 2: Select size tier ---
    cost_matrix = data["cost_matrix"][type_id]
    size_tiers = data["size_tiers"]

    selected_tier = None
    for tier in reversed(size_tiers):
        tier_costs = cost_matrix.get(tier["id"])
        if tier_costs and tier_costs["total_diy_low"] <= budget_ceiling:
            selected_tier = tier
            trace.append(f"Size: Selected '{tier['id']}' based on ${tier_costs['total_diy_low']:,} DIY cost fitting under ${budget_ceiling:,} ceiling")
            break

    if selected_tier is None:
        selected_tier = size_tiers[0]
        trace.append(f"Size: Defaulted to '{selected_tier['id']}' because no larger tier fit budget")

    # Property constraint: backyard caps at "serious"
    if prop == "backyard" and selected_tier["id"] == "market":
        selected_tier = size_tiers[2]
        trace.append("Size: Capped at 'serious' (backyard property constraint)")

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

    # Dynamic reasoning text
    reasoning_parts = []
    reasoning_parts.append(f"A {selected_type['name']} is the best match for your {climate['label']} location.")
    
    if gh_pref == "not_sure":
        if budget == "under_5k":
            reasoning_parts.append("Given your budget, a high-efficiency polytunnel provides the best growth-to-cost ratio.")
        elif selected_type['id'] == "passive_solar":
            reasoning_parts.append("We recommended passive solar because it directly supports your goal of sustainability and self-reliance in the NS climate.")
        else:
            reasoning_parts.append("Polycarbonate offers the best balance of insulation and durability for standard backyard setups.")
    else:
        reasoning_parts.append(f"We've optimized the plan based on your preference for a {selected_type['name']} structure.")

    reasoning_parts.append(f"The {selected_tier['dimensions']} size gives you {selected_tier['beds']} with capacity for {selected_tier['capacity']}.")

    why = " ".join(reasoning_parts)

    # --- Step 4: Calculate Impact ---
    sqft = selected_tier["sq_ft"]
    if sqft >= 350:
        impact = {"produce": "50–80%", "savings": "$1,500–$2,500"}
    elif sqft >= 250:
        impact = {"produce": "40–60%", "savings": "$1,000–$1,800"}
    elif sqft >= 150:
        impact = {"produce": "25–45%", "savings": "$600–$1,200"}
    else:
        impact = {"produce": "15–30%", "savings": "$300–$700"}

    return {
        "recommendation": f"{selected_tier['dimensions']} {selected_type['name']}",
        "why": why,
        "trace": trace,
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
        "impact": impact,
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
