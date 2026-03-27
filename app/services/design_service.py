"""Design Service — selects ONE greenhouse archetype via flat lookup table.

Replaces the previous binary logic with a deterministic selection matrix
mapping (budget, property_type, greenhouse_type, goal, wind_exposure,
has_south_wall, experience_level) → archetype ID.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services.archetypes import get_archetype

_DATA: dict = {}


def _load_data():
    global _DATA
    if not _DATA:
        path = Path(__file__).resolve().parents[2] / "config" / "greenhouse_data.json"
        with open(path, "r", encoding="utf-8") as f:
            _DATA = json.load(f)
    return _DATA


# ── Disqualification rules (checked first, in order) ─────────────────────

def _apply_disqualifications(
    budget: str,
    wind_exposure: str,
    has_south_wall: str,
    property_type: str,
    experience_level: str,
) -> str | None:
    """Return an archetype ID if a hard disqualification rule fires, else None."""

    # Budget under $1K equivalent → always Cold Frame Bridge
    if budget == "under_5k" and wind_exposure == "coastal_exposed":
        return "cold_frame_bridge"

    # Small lot with tight budget → Cold Frame Bridge
    if budget == "under_5k" and property_type == "small_lot":
        return "cold_frame_bridge"

    # Coastal exposed must be at least Maritime Standard (never Starter Kit)
    # This is handled in the main lookup by ensuring coastal rows map correctly

    return None


# ── Flat lookup table ────────────────────────────────────────────────────
# Key: (budget, property_type, greenhouse_preference, goal)
# Value: archetype ID
#
# When wind_exposure == "coastal_exposed", Starter Kit is upgraded to
# Maritime Standard in a post-lookup override.
#
# When has_south_wall == "no", passive_solar_leanto is downgraded to
# maritime_standard.

_LOOKUP: dict[tuple[str, str, str, str], str] = {
    # ── Budget: under_5k ──────────────────────────────────────────────
    # Most under_5k users get Starter Kit (sheltered) or Cold Frame Bridge (exposed)
    ("under_5k", "backyard",  "not_sure",       "grow_food"):       "starter_kit",
    ("under_5k", "backyard",  "not_sure",       "save_money"):      "starter_kit",
    ("under_5k", "backyard",  "not_sure",       "sustainability"):  "starter_kit",
    ("under_5k", "backyard",  "not_sure",       "mixed"):           "starter_kit",
    ("under_5k", "backyard",  "polycarbonate",  "grow_food"):       "starter_kit",
    ("under_5k", "backyard",  "polycarbonate",  "save_money"):      "starter_kit",
    ("under_5k", "backyard",  "polycarbonate",  "sustainability"):  "starter_kit",
    ("under_5k", "backyard",  "polycarbonate",  "mixed"):           "starter_kit",
    ("under_5k", "backyard",  "polytunnel",     "grow_food"):       "starter_kit",
    ("under_5k", "backyard",  "polytunnel",     "save_money"):      "starter_kit",
    ("under_5k", "backyard",  "polytunnel",     "sustainability"):  "starter_kit",
    ("under_5k", "backyard",  "polytunnel",     "mixed"):           "starter_kit",
    ("under_5k", "backyard",  "passive_solar",  "grow_food"):       "starter_kit",
    ("under_5k", "backyard",  "passive_solar",  "save_money"):      "starter_kit",
    ("under_5k", "backyard",  "passive_solar",  "sustainability"):  "starter_kit",
    ("under_5k", "backyard",  "passive_solar",  "mixed"):           "starter_kit",
    ("under_5k", "rural",     "not_sure",       "grow_food"):       "starter_kit",
    ("under_5k", "rural",     "not_sure",       "save_money"):      "starter_kit",
    ("under_5k", "rural",     "not_sure",       "sustainability"):  "starter_kit",
    ("under_5k", "rural",     "not_sure",       "mixed"):           "starter_kit",
    ("under_5k", "rural",     "polycarbonate",  "grow_food"):       "starter_kit",
    ("under_5k", "rural",     "polycarbonate",  "save_money"):      "starter_kit",
    ("under_5k", "rural",     "polycarbonate",  "sustainability"):  "starter_kit",
    ("under_5k", "rural",     "polycarbonate",  "mixed"):           "starter_kit",
    ("under_5k", "rural",     "polytunnel",     "grow_food"):       "starter_kit",
    ("under_5k", "rural",     "polytunnel",     "save_money"):      "starter_kit",
    ("under_5k", "rural",     "polytunnel",     "sustainability"):  "starter_kit",
    ("under_5k", "rural",     "polytunnel",     "mixed"):           "starter_kit",
    ("under_5k", "rural",     "passive_solar",  "grow_food"):       "starter_kit",
    ("under_5k", "rural",     "passive_solar",  "save_money"):      "starter_kit",
    ("under_5k", "rural",     "passive_solar",  "sustainability"):  "starter_kit",
    ("under_5k", "rural",     "passive_solar",  "mixed"):           "starter_kit",
    ("under_5k", "small_lot", "not_sure",       "grow_food"):       "cold_frame_bridge",
    ("under_5k", "small_lot", "not_sure",       "save_money"):      "cold_frame_bridge",
    ("under_5k", "small_lot", "not_sure",       "sustainability"):  "cold_frame_bridge",
    ("under_5k", "small_lot", "not_sure",       "mixed"):           "cold_frame_bridge",
    ("under_5k", "small_lot", "polycarbonate",  "grow_food"):       "starter_kit",
    ("under_5k", "small_lot", "polycarbonate",  "save_money"):      "starter_kit",
    ("under_5k", "small_lot", "polycarbonate",  "sustainability"):  "starter_kit",
    ("under_5k", "small_lot", "polycarbonate",  "mixed"):           "starter_kit",
    ("under_5k", "small_lot", "polytunnel",     "grow_food"):       "cold_frame_bridge",
    ("under_5k", "small_lot", "polytunnel",     "save_money"):      "cold_frame_bridge",
    ("under_5k", "small_lot", "polytunnel",     "sustainability"):  "cold_frame_bridge",
    ("under_5k", "small_lot", "polytunnel",     "mixed"):           "cold_frame_bridge",
    ("under_5k", "small_lot", "passive_solar",  "grow_food"):       "starter_kit",
    ("under_5k", "small_lot", "passive_solar",  "save_money"):      "starter_kit",
    ("under_5k", "small_lot", "passive_solar",  "sustainability"):  "starter_kit",
    ("under_5k", "small_lot", "passive_solar",  "mixed"):           "starter_kit",
    ("under_5k", "not_sure",  "not_sure",       "grow_food"):       "starter_kit",
    ("under_5k", "not_sure",  "not_sure",       "save_money"):      "starter_kit",
    ("under_5k", "not_sure",  "not_sure",       "sustainability"):  "starter_kit",
    ("under_5k", "not_sure",  "not_sure",       "mixed"):           "starter_kit",
    ("under_5k", "not_sure",  "polycarbonate",  "grow_food"):       "starter_kit",
    ("under_5k", "not_sure",  "polycarbonate",  "save_money"):      "starter_kit",
    ("under_5k", "not_sure",  "polycarbonate",  "sustainability"):  "starter_kit",
    ("under_5k", "not_sure",  "polycarbonate",  "mixed"):           "starter_kit",
    ("under_5k", "not_sure",  "polytunnel",     "grow_food"):       "starter_kit",
    ("under_5k", "not_sure",  "polytunnel",     "save_money"):      "starter_kit",
    ("under_5k", "not_sure",  "polytunnel",     "sustainability"):  "starter_kit",
    ("under_5k", "not_sure",  "polytunnel",     "mixed"):           "starter_kit",
    ("under_5k", "not_sure",  "passive_solar",  "grow_food"):       "starter_kit",
    ("under_5k", "not_sure",  "passive_solar",  "save_money"):      "starter_kit",
    ("under_5k", "not_sure",  "passive_solar",  "sustainability"):  "starter_kit",
    ("under_5k", "not_sure",  "passive_solar",  "mixed"):           "starter_kit",

    # ── Budget: 5k_10k ───────────────────────────────────────────────
    ("5k_10k", "backyard",  "not_sure",       "grow_food"):       "maritime_standard",
    ("5k_10k", "backyard",  "not_sure",       "save_money"):      "maritime_standard",
    ("5k_10k", "backyard",  "not_sure",       "sustainability"):  "maritime_standard",
    ("5k_10k", "backyard",  "not_sure",       "mixed"):           "maritime_standard",
    ("5k_10k", "backyard",  "polycarbonate",  "grow_food"):       "maritime_standard",
    ("5k_10k", "backyard",  "polycarbonate",  "save_money"):      "maritime_standard",
    ("5k_10k", "backyard",  "polycarbonate",  "sustainability"):  "maritime_standard",
    ("5k_10k", "backyard",  "polycarbonate",  "mixed"):           "maritime_standard",
    ("5k_10k", "backyard",  "polytunnel",     "grow_food"):       "maritime_standard",
    ("5k_10k", "backyard",  "polytunnel",     "save_money"):      "maritime_standard",
    ("5k_10k", "backyard",  "polytunnel",     "sustainability"):  "maritime_standard",
    ("5k_10k", "backyard",  "polytunnel",     "mixed"):           "maritime_standard",
    ("5k_10k", "backyard",  "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("5k_10k", "backyard",  "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("5k_10k", "backyard",  "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("5k_10k", "backyard",  "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("5k_10k", "rural",     "not_sure",       "grow_food"):       "maritime_standard",
    ("5k_10k", "rural",     "not_sure",       "save_money"):      "maritime_standard",
    ("5k_10k", "rural",     "not_sure",       "sustainability"):  "passive_solar_leanto",
    ("5k_10k", "rural",     "not_sure",       "mixed"):           "maritime_standard",
    ("5k_10k", "rural",     "polycarbonate",  "grow_food"):       "maritime_standard",
    ("5k_10k", "rural",     "polycarbonate",  "save_money"):      "maritime_standard",
    ("5k_10k", "rural",     "polycarbonate",  "sustainability"):  "maritime_standard",
    ("5k_10k", "rural",     "polycarbonate",  "mixed"):           "maritime_standard",
    ("5k_10k", "rural",     "polytunnel",     "grow_food"):       "maritime_standard",
    ("5k_10k", "rural",     "polytunnel",     "save_money"):      "maritime_standard",
    ("5k_10k", "rural",     "polytunnel",     "sustainability"):  "maritime_standard",
    ("5k_10k", "rural",     "polytunnel",     "mixed"):           "maritime_standard",
    ("5k_10k", "rural",     "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("5k_10k", "rural",     "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("5k_10k", "rural",     "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("5k_10k", "rural",     "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("5k_10k", "small_lot", "not_sure",       "grow_food"):       "starter_kit",
    ("5k_10k", "small_lot", "not_sure",       "save_money"):      "starter_kit",
    ("5k_10k", "small_lot", "not_sure",       "sustainability"):  "starter_kit",
    ("5k_10k", "small_lot", "not_sure",       "mixed"):           "starter_kit",
    ("5k_10k", "small_lot", "polycarbonate",  "grow_food"):       "starter_kit",
    ("5k_10k", "small_lot", "polycarbonate",  "save_money"):      "starter_kit",
    ("5k_10k", "small_lot", "polycarbonate",  "sustainability"):  "starter_kit",
    ("5k_10k", "small_lot", "polycarbonate",  "mixed"):           "starter_kit",
    ("5k_10k", "small_lot", "polytunnel",     "grow_food"):       "starter_kit",
    ("5k_10k", "small_lot", "polytunnel",     "save_money"):      "starter_kit",
    ("5k_10k", "small_lot", "polytunnel",     "sustainability"):  "starter_kit",
    ("5k_10k", "small_lot", "polytunnel",     "mixed"):           "starter_kit",
    ("5k_10k", "small_lot", "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("5k_10k", "small_lot", "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("5k_10k", "small_lot", "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("5k_10k", "small_lot", "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("5k_10k", "not_sure",  "not_sure",       "grow_food"):       "maritime_standard",
    ("5k_10k", "not_sure",  "not_sure",       "save_money"):      "maritime_standard",
    ("5k_10k", "not_sure",  "not_sure",       "sustainability"):  "maritime_standard",
    ("5k_10k", "not_sure",  "not_sure",       "mixed"):           "maritime_standard",
    ("5k_10k", "not_sure",  "polycarbonate",  "grow_food"):       "maritime_standard",
    ("5k_10k", "not_sure",  "polycarbonate",  "save_money"):      "maritime_standard",
    ("5k_10k", "not_sure",  "polycarbonate",  "sustainability"):  "maritime_standard",
    ("5k_10k", "not_sure",  "polycarbonate",  "mixed"):           "maritime_standard",
    ("5k_10k", "not_sure",  "polytunnel",     "grow_food"):       "maritime_standard",
    ("5k_10k", "not_sure",  "polytunnel",     "save_money"):      "maritime_standard",
    ("5k_10k", "not_sure",  "polytunnel",     "sustainability"):  "maritime_standard",
    ("5k_10k", "not_sure",  "polytunnel",     "mixed"):           "maritime_standard",
    ("5k_10k", "not_sure",  "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("5k_10k", "not_sure",  "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("5k_10k", "not_sure",  "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("5k_10k", "not_sure",  "passive_solar",  "mixed"):           "passive_solar_leanto",

    # ── Budget: over_10k ─────────────────────────────────────────────
    ("over_10k", "backyard",  "not_sure",       "grow_food"):       "maritime_standard",
    ("over_10k", "backyard",  "not_sure",       "save_money"):      "maritime_standard",
    ("over_10k", "backyard",  "not_sure",       "sustainability"):  "passive_solar_leanto",
    ("over_10k", "backyard",  "not_sure",       "mixed"):           "maritime_standard",
    ("over_10k", "backyard",  "polycarbonate",  "grow_food"):       "maritime_standard",
    ("over_10k", "backyard",  "polycarbonate",  "save_money"):      "maritime_standard",
    ("over_10k", "backyard",  "polycarbonate",  "sustainability"):  "maritime_standard",
    ("over_10k", "backyard",  "polycarbonate",  "mixed"):           "maritime_standard",
    ("over_10k", "backyard",  "polytunnel",     "grow_food"):       "maritime_standard",
    ("over_10k", "backyard",  "polytunnel",     "save_money"):      "maritime_standard",
    ("over_10k", "backyard",  "polytunnel",     "sustainability"):  "maritime_standard",
    ("over_10k", "backyard",  "polytunnel",     "mixed"):           "maritime_standard",
    ("over_10k", "backyard",  "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("over_10k", "backyard",  "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("over_10k", "backyard",  "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("over_10k", "backyard",  "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("over_10k", "rural",     "not_sure",       "grow_food"):       "serious_grower",
    ("over_10k", "rural",     "not_sure",       "save_money"):      "serious_grower",
    ("over_10k", "rural",     "not_sure",       "sustainability"):  "passive_solar_leanto",
    ("over_10k", "rural",     "not_sure",       "mixed"):           "serious_grower",
    ("over_10k", "rural",     "polycarbonate",  "grow_food"):       "serious_grower",
    ("over_10k", "rural",     "polycarbonate",  "save_money"):      "serious_grower",
    ("over_10k", "rural",     "polycarbonate",  "sustainability"):  "serious_grower",
    ("over_10k", "rural",     "polycarbonate",  "mixed"):           "serious_grower",
    ("over_10k", "rural",     "polytunnel",     "grow_food"):       "serious_grower",
    ("over_10k", "rural",     "polytunnel",     "save_money"):      "serious_grower",
    ("over_10k", "rural",     "polytunnel",     "sustainability"):  "serious_grower",
    ("over_10k", "rural",     "polytunnel",     "mixed"):           "serious_grower",
    ("over_10k", "rural",     "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("over_10k", "rural",     "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("over_10k", "rural",     "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("over_10k", "rural",     "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("over_10k", "small_lot", "not_sure",       "grow_food"):       "maritime_standard",
    ("over_10k", "small_lot", "not_sure",       "save_money"):      "maritime_standard",
    ("over_10k", "small_lot", "not_sure",       "sustainability"):  "passive_solar_leanto",
    ("over_10k", "small_lot", "not_sure",       "mixed"):           "maritime_standard",
    ("over_10k", "small_lot", "polycarbonate",  "grow_food"):       "maritime_standard",
    ("over_10k", "small_lot", "polycarbonate",  "save_money"):      "maritime_standard",
    ("over_10k", "small_lot", "polycarbonate",  "sustainability"):  "maritime_standard",
    ("over_10k", "small_lot", "polycarbonate",  "mixed"):           "maritime_standard",
    ("over_10k", "small_lot", "polytunnel",     "grow_food"):       "maritime_standard",
    ("over_10k", "small_lot", "polytunnel",     "save_money"):      "maritime_standard",
    ("over_10k", "small_lot", "polytunnel",     "sustainability"):  "maritime_standard",
    ("over_10k", "small_lot", "polytunnel",     "mixed"):           "maritime_standard",
    ("over_10k", "small_lot", "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("over_10k", "small_lot", "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("over_10k", "small_lot", "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("over_10k", "small_lot", "passive_solar",  "mixed"):           "passive_solar_leanto",
    ("over_10k", "not_sure",  "not_sure",       "grow_food"):       "maritime_standard",
    ("over_10k", "not_sure",  "not_sure",       "save_money"):      "maritime_standard",
    ("over_10k", "not_sure",  "not_sure",       "sustainability"):  "passive_solar_leanto",
    ("over_10k", "not_sure",  "not_sure",       "mixed"):           "maritime_standard",
    ("over_10k", "not_sure",  "polycarbonate",  "grow_food"):       "maritime_standard",
    ("over_10k", "not_sure",  "polycarbonate",  "save_money"):      "maritime_standard",
    ("over_10k", "not_sure",  "polycarbonate",  "sustainability"):  "maritime_standard",
    ("over_10k", "not_sure",  "polycarbonate",  "mixed"):           "maritime_standard",
    ("over_10k", "not_sure",  "polytunnel",     "grow_food"):       "maritime_standard",
    ("over_10k", "not_sure",  "polytunnel",     "save_money"):      "maritime_standard",
    ("over_10k", "not_sure",  "polytunnel",     "sustainability"):  "maritime_standard",
    ("over_10k", "not_sure",  "polytunnel",     "mixed"):           "maritime_standard",
    ("over_10k", "not_sure",  "passive_solar",  "grow_food"):       "passive_solar_leanto",
    ("over_10k", "not_sure",  "passive_solar",  "save_money"):      "passive_solar_leanto",
    ("over_10k", "not_sure",  "passive_solar",  "sustainability"):  "passive_solar_leanto",
    ("over_10k", "not_sure",  "passive_solar",  "mixed"):           "passive_solar_leanto",
}


def recommend_design(intake: dict, suitability: dict) -> dict:
    """
    Produce ONE greenhouse archetype recommendation based on intake + suitability.

    Selection priority:
    1. Hard disqualification rules (budget/exposure combos)
    2. Flat lookup table on (budget, property, preference, goal)
    3. Post-lookup overrides for wind exposure and south wall
    4. Experience-level adjustments to confidence scores
    """
    data = _load_data()
    budget = intake.get("budget", "under_5k")
    goal = intake.get("goal", "grow_food")
    prop = intake.get("property_type", "backyard")
    gh_pref = intake.get("greenhouse_type", "not_sure")
    wind = intake.get("wind_exposure", "moderate")
    south_wall = intake.get("has_south_wall", "not_sure")
    experience = intake.get("experience_level", "first_time")
    climate = suitability["climate"]

    # ── Step 1: Hard disqualification ────────────────────────────────
    disqualified_id = _apply_disqualifications(
        budget, wind, south_wall, prop, experience
    )

    if disqualified_id:
        archetype = get_archetype(disqualified_id)
    else:
        # ── Step 2: Lookup table ─────────────────────────────────────
        key = (budget, prop, gh_pref, goal)
        archetype_id = _LOOKUP.get(key, "maritime_standard")
        archetype = get_archetype(archetype_id)

    # ── Step 3: Post-lookup overrides ────────────────────────────────
    archetype_id = archetype["id"]

    # Coastal exposure: upgrade Starter Kit → Maritime Standard
    if wind == "coastal_exposed" and archetype_id == "starter_kit":
        archetype = get_archetype("maritime_standard")
        archetype_id = "maritime_standard"

    # No south wall: downgrade Passive Solar → Maritime Standard
    if south_wall == "no" and archetype_id == "passive_solar_leanto":
        archetype = get_archetype("maritime_standard")
        archetype_id = "maritime_standard"

    # First-time grower: don't recommend Serious Grower
    if experience == "first_time" and archetype_id == "serious_grower":
        archetype = get_archetype("maritime_standard")
        archetype_id = "maritime_standard"

    # not_sure south wall: deprioritize passive solar with lowered confidence
    confidence_overrides = {}
    if south_wall == "not_sure" and archetype_id == "passive_solar_leanto":
        confidence_overrides["site_fit_confidence"] = "low"

    # ── Step 4: Build the full response ──────────────────────────────
    # Make a copy so we don't mutate the archetype definition
    result = dict(archetype)

    # Remove internal keys from response
    result.pop("_legacy_type_id", None)
    result.pop("_legacy_tier_id", None)

    # Apply any confidence overrides
    for k, v in confidence_overrides.items():
        result[k] = v

    # Attach climate context
    result["climate_context"] = {
        "zone": climate["zone"],
        "region": climate["label"],
        "last_frost": climate["avg_last_frost"],
        "first_frost": climate["avg_first_frost"],
        "growing_season": climate["growing_season_days"],
        "snow_load": climate["design_snow_load_psf"],
        "frost_depth": climate["frost_depth_inches"],
    }

    # Attach selection metadata (for downstream services and frontend)
    result["selection_context"] = {
        "wind_exposure": wind,
        "has_south_wall": south_wall,
        "experience_level": experience,
        "budget_input": budget,
        "property_type": prop,
        "greenhouse_preference": gh_pref,
        "goal": goal,
        "location": intake.get("location", "halifax"),
    }

    # Legacy mapping for cost_service and crop_service compatibility
    result["greenhouse"] = {
        "type_id": archetype.get("_legacy_type_id", "polycarbonate"),
    }
    result["size"] = {
        "tier_id": archetype.get("_legacy_tier_id", "starter"),
    }

    return result
